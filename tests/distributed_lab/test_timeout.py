import time
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import httpx
import pytest
from threading import Lock
from lab_fw.api.client import ApiClient
from lab_fw.core.config import Settings
from lab_fw.core.errors import ApiError
from distributed_lab.queue_worker import Job, InMemoryQueue, parse_job, Worker
from lab_fw.core.errors import JobDeadlineExceeded, WorkerDeadlineExceeded
import sys
import json
from urllib.parse import urlsplit
import re

def wait_for_server(host: str, port: int, timeout: float = 2.0) -> None:
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.1):
                return
        except OSError:
            time.sleep(0.01)

    raise TimeoutError(f"Server {host}:{port} did not become ready")

def wait_for_http_server(
    base_url: str,
    timeout: float = 2.0,
) -> None:
    deadline = time.monotonic() + timeout

    with httpx.Client(timeout=0.2) as client:
        while time.monotonic() < deadline:
            try:
                response = client.get(f"{base_url}/health")

                if response.status_code == 200 and response.text == "OK":
                    return

            except httpx.RequestError:
                pass

            time.sleep(0.01)

    raise TimeoutError(f"HTTP server {base_url} did not become ready")

class SlowTestServer(ThreadingHTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.request_counts = {}
        self.lock = Lock()

class SlowHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            return
        self.server.last_handler = self

        with self.server.lock:
            self.server.request_counts[self.path] =  self.server.request_counts.get(self.path, 0) + 1
        time.sleep(0.5)
        try:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, format, *args):
        pass

@pytest.mark.distributed_lab
def test_api_client_timeout():
    server = SlowTestServer(("127.0.0.1", 0), SlowHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        wait_for_server("127.0.0.1", server.server_port)
        wait_for_http_server(base_url)
        client = None
        client_ = None
        client = ApiClient(
            Settings(
                base_url=base_url,
                timeout_s=0.1,
                log_level="INFO",
            )
        )

        client_ = ApiClient(
                Settings(
                    base_url=base_url,
                    timeout_s=1,
                    log_level="INFO",
                )
            )

    
        
        with pytest.raises(ApiError) as exc_info:
            client.get("/slow")

        assert exc_info.value.__cause__ is not None
        assert "ReadTimeout" in type(exc_info.value.__cause__).__name__
        assert isinstance(exc_info.value.__cause__, httpx.ReadTimeout)

        response = client_.get("/slow")
        assert response.status_code == 200
        assert response.text == "OK"
        assert response.reason_phrase == "OK"
        assert response.request.method == "GET"
        assert response.request.url.path == "/slow"
        assert response.request.url.scheme == "http"
        assert response.request.url.host == "127.0.0.1"
        assert response.request.url.port == server.server_port
        assert response.request.url.path == "/slow"
        assert str(response.request.url) == f"http://127.0.0.1:{server.server_port}/slow"
        assert response.request.extensions["timeout"]["read"] == 1
        assert response.request.extensions["timeout"] == {
                                                            "connect": 1.0,
                                                            "read": 1.0,
                                                            "write": 1.0,
                                                            "pool": 1.0,
                                                        }
        assert response.request.extensions["timeout"]["connect"] == 1.0
        assert response.request.extensions["timeout"]["read"] == 1.0
        assert response.request.extensions["timeout"]["write"] == 1.0
        assert response.request.extensions["timeout"]["pool"] == 1.0
    finally:
        if client is not None:
            client.close()
        if client_ is not None:
            client_.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

@pytest.mark.distributed_lab
def test_worker_retries_after_timeout():
    server = SlowTestServer(("127.0.0.1", 0), SlowHandler)
    
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        wait_for_server("127.0.0.1", server.server_port)
        wait_for_http_server(base_url)
        client = None
        client = ApiClient(
            Settings(
                base_url=base_url,
                timeout_s=0.1,
                log_level="INFO",
            )
        )

        queue = InMemoryQueue()
        queue.put(parse_job({"method": "GET", "path": "/slow"}))
        queue.put(parse_job({"method": "GET", "path": "/slow/2", "timeout": 1}))
        worker = Worker(queue, client)
        
        with pytest.raises(ApiError) as exc_info:
            worker.run_once()

        assert isinstance(exc_info.value.__cause__, httpx.ReadTimeout)
        assert isinstance(exc_info.value, ApiError)
        assert exc_info.value.__cause__.request.method == "GET"
        assert exc_info.value.__cause__.request.url.path == "/slow"
        assert server.request_counts["/slow"] == 3
        assert isinstance(server, ThreadingHTTPServer)
        assert server.RequestHandlerClass is SlowHandler
        assert server.server_address[0] == "127.0.0.1"
        assert server.server_address[1] == server.server_port
        assert server.server_port > 0
        assert server.socket is not None
        assert server.server_name
        assert isinstance(server.server_name, str)
        assert server.RequestHandlerClass is SlowHandler
        assert server.RequestHandlerClass.__name__ == "SlowHandler"
        assert server.RequestHandlerClass.__module__ == SlowHandler.__module__
        assert callable(server.RequestHandlerClass.do_GET)
        assert callable(server.RequestHandlerClass.log_message)

        handler = server.last_handler
        assert isinstance(handler, SlowHandler)
        assert handler is server.last_handler
        assert handler.server is server
        assert handler.path == "/slow"
        assert handler.command == "GET"
        assert handler.request_version == "HTTP/1.1"
        assert handler.requestline == "GET /slow HTTP/1.1"
        assert handler.headers["Host"] == f"127.0.0.1:{server.server_port}"
        assert handler.headers["User-Agent"].startswith("python-httpx/")
        assert handler.headers["Accept"] == "*/*"
        assert handler.headers["Connection"] == "keep-alive"
        assert handler.client_address[0] == "127.0.0.1"
        assert isinstance(handler.client_address[1], int)
        assert handler.client_address[1] > 0
        assert handler.server is server
        assert handler.rfile is not None
        assert handler.wfile is not None
   
        response = worker.run_once()
        handler = server.last_handler
        assert response.status_code == 200
        assert response.text == "OK"
        assert response.request.method == "GET"
        assert response.request.url.path == "/slow/2"
        assert response.request.extensions["timeout"]["connect"] == 1.0
        assert response.request.extensions["timeout"]["read"] == 1.0
        assert response.request.extensions["timeout"]["write"] == 1.0
        assert response.request.extensions["timeout"]["pool"] == 1.0
        assert server.request_counts["/slow/2"] == 1
        
        assert isinstance(handler, SlowHandler)
        assert handler is server.last_handler
        assert handler.server is server
        assert handler.path == "/slow/2"
        assert handler.command == "GET"
        assert handler.request_version == "HTTP/1.1"
        assert handler.requestline == "GET /slow/2 HTTP/1.1"
        assert handler.headers["Host"] == f"127.0.0.1:{server.server_port}"
        assert handler.headers["User-Agent"].startswith("python-httpx/")
        assert handler.headers["Accept"] == "*/*"
        assert handler.headers["Connection"] == "keep-alive"
        assert handler.client_address[0] == "127.0.0.1"
        assert isinstance(handler.client_address[1], int)
        assert handler.client_address[1] > 0
        assert handler.server is server
        assert handler.rfile is not None
        assert handler.wfile is not None
        
    finally:
        if client is not None:
            client.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

@pytest.mark.distributed_lab
def test_worker_retries_default_timeout():
    server = SlowTestServer(("127.0.0.1", 0), SlowHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        wait_for_server("127.0.0.1", server.server_port)
        wait_for_http_server(base_url)
        client = None

        client = ApiClient(
            Settings(
                base_url=base_url,
                timeout_s=1,
                log_level="INFO",
            )
        )

        queue = InMemoryQueue()
        queue.put(parse_job({"method": "GET", "path": "/slow"}))
        worker = Worker(queue, client)
    
        
        response = worker.run_once()
        assert response.status_code == 200
        assert response.request.method == "GET"
        assert response.request.url.path == "/slow"
        assert response.request.extensions["timeout"]["connect"] == 1.0
        assert response.request.extensions["timeout"]["read"] == 1.0
        assert response.request.extensions["timeout"]["write"] == 1.0
        assert response.request.extensions["timeout"]["pool"] == 1.0
    finally:
        if client is not None:
            client.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.mark.distributed_lab
def test_worker_rejects_expired_job_deadline():
    client = ApiClient(
        Settings(
            base_url="http://127.0.0.1:1",
            timeout_s=1,
            log_level="INFO",
        )
    )

    queue = InMemoryQueue()
    queue.put(
        parse_job({
            "method": "GET",
            "path": "/should-not-run",
            "deadline_s": 0.0,
        })
    )
    worker = Worker(queue, client)

    try:
        with pytest.raises(JobDeadlineExceeded, match="Job deadline exceeded"):
            worker.run_once()
    finally:
        client.close()

@pytest.mark.distributed_lab
def test_worker_rejects_expired_job_deadline_without_http_call():

    settings = Settings(
                            base_url="http://127.0.0.1:1",
                            timeout_s=1,
                            log_level="INFO",
                        )
                
    captured_request = None
    
    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json={"items": [1, 2]})

    transport = httpx.MockTransport(handler)

    queue = InMemoryQueue()
    queue.put(
        parse_job({
            "method": "GET",
            "path": "/should-not-run",
            "deadline_s": 0.0,
        })
    )
    response = None
    with ApiClient(settings, transport=transport) as client:
        assert len(queue._queue) == 1
        worker = Worker(queue, client)
        with pytest.raises(JobDeadlineExceeded, match="Job deadline exceeded"):
            response = worker.run_once()
    assert response is None
    assert captured_request is None
    assert len(queue._queue) == 0
        

@pytest.mark.distributed_lab
def test_worker_stops_retries_after_job_deadline():
    server = SlowTestServer(("127.0.0.1", 0), SlowHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        wait_for_server("127.0.0.1", server.server_port)
        wait_for_http_server(base_url)
        client = None

        client = ApiClient(
            Settings(
                base_url=base_url,
                timeout_s=1,
                log_level="INFO",
            )
        )

        queue = InMemoryQueue()
        queue.put(
            parse_job({
                "method": "GET",
                "path": "/slow",
                "deadline_s": 0.15,
            })
        )
        worker = Worker(queue, client)

    
        with pytest.raises(JobDeadlineExceeded):
            worker.run_once()

        assert server.request_counts["/slow"] == 1
    finally:
        if client is not None:
            client.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)



@pytest.mark.distributed_lab
def test_worker_stops_3_retries_after_job_deadline():
    server = SlowTestServer(("127.0.0.1", 0), SlowHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        wait_for_server("127.0.0.1", server.server_port)
        wait_for_http_server(base_url)
        client = None
        client = ApiClient(
            Settings(
                base_url=base_url,
                timeout_s=1,
                log_level="INFO",
            )
        )

        queue = InMemoryQueue()
        queue.put(
            parse_job({
                "method": "GET",
                "path": "/slow",
                "timeout": 0.1,
                "deadline_s": 0.45,
            })
        )
        worker = Worker(queue, client)

    
        with pytest.raises(ApiError):
            worker.run_once()

        assert server.request_counts["/slow"] == 3
    finally:
        if client is not None:
            client.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.mark.distributed_lab
def test_worker_deadline_error_overrides_final_api_error():
    server = SlowTestServer(("127.0.0.1", 0), SlowHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        wait_for_server("127.0.0.1", server.server_port)
        wait_for_http_server(base_url)
        client = None
        client = ApiClient(
            Settings(
                base_url=base_url,
                timeout_s=1,
                log_level="INFO",
            )
        )

        queue = InMemoryQueue()
        queue.put(
            parse_job({
                "method": "GET",
                "path": "/slow",
                "timeout": 0.2,
                "deadline_s": 0.45,
            })
        )
        worker = Worker(queue, client)

    
        with pytest.raises(JobDeadlineExceeded):
            worker.run_once()

        assert server.request_counts["/slow"] <= 3
        assert server.request_counts["/slow"] >= 1
    finally:
        if client is not None:
            client.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.mark.distributed_lab
def test_worker_does_not_retry_after_deadline_expires(monkeypatch):
    queue = InMemoryQueue()
    queue.put(
        parse_job({
            "method": "GET",
            "path": "/slow",
            "deadline_s": 10.0,
        })
    )

    calls = 0
    clock_values = iter([100.0, 100.0, 100.0, 111.0])

    monkeypatch.setattr(
                        time,
                        "monotonic",
                        lambda: next(clock_values),
                    )

    class FakeApiClient:
        def get(self, path, **kwargs):
            nonlocal calls
            calls += 1
            request = httpx.Request("GET", "http://example.com/slow")
            cause = httpx.ReadTimeout("Request timed out", request=request)
            raise ApiError("Request failed") from cause

    monkeypatch.setattr(
                            sys.modules[__name__],
                            "ApiClient",
                            FakeApiClient,
                        )

    worker = Worker(queue, ApiClient())

    with pytest.raises(JobDeadlineExceeded):
        worker.run_once()

    assert calls == 1

@pytest.mark.distributed_lab
def test_worker_does_not_retry_after_deadline_expires_(monkeypatch):
    import distributed_lab.queue_worker as worker_module

    queue = InMemoryQueue()
    queue.put(
        parse_job({
            "method": "GET",
            "path": "/test",
            "deadline_s": 5.0,
        })
    )

    worker = Worker(queue, api_client=None)
    clock = iter([100.0, 100.0, 106.0])
    calls = 0

    def fake_monotonic():
        value = next(clock)
        print(f"monotonic() -> {value}")
        return value

    monkeypatch.setattr(
        worker_module.time,
        "monotonic",
        fake_monotonic,
    )

    #monkeypatch.setattr(worker_module.time, "monotonic", lambda: next(clock))

    def fail_request(*args, **kwargs):
        nonlocal calls
        calls += 1

        request = httpx.Request("GET", "http://example.com/test")
        cause = httpx.ReadTimeout("Request timed out", request=request)
        raise ApiError("Request failed") from cause
    
    monkeypatch.setattr(worker_module.Worker, "execute", fail_request)

    with pytest.raises(JobDeadlineExceeded):
        worker.run_once()

    assert calls == 1

@pytest.mark.distributed_lab
def test_worker_deadline_expires_before_job(monkeypatch):
    queue = InMemoryQueue()
    queue.put(
        parse_job({
            "method": "GET",
            "path": "/test",
        })
    )

    calls = 0

    class FakeApiClient:
        def get(self, path, **kwargs):
            nonlocal calls
            calls += 1
            request = httpx.Request("GET", "http://example.com/slow")
            cause = httpx.ReadTimeout("Request timed out", request=request)
            raise ApiError("Request failed") from cause

    monkeypatch.setattr(
                            sys.modules[__name__],
                            "ApiClient",
                            FakeApiClient,
                        )

    worker = Worker(queue, ApiClient(), 0)

    with pytest.raises(WorkerDeadlineExceeded):
        worker.run_once()
    
    assert queue.get() is not None
    assert calls == 0

@pytest.mark.distributed_lab
def test_worker_timeout_limited_by_worker_deadline(monkeypatch):
    
    queue = InMemoryQueue()
    queue.put(Job(method="GET", path="/test", timeout=5.0))

    expected_response = httpx.Response(200)
    calls = []

    class FakeApiClient:
        def get(self, path, **kwargs):
            calls.append((path, kwargs))
            return expected_response

    monkeypatch.setattr(
                            sys.modules[__name__],
                            "ApiClient",
                            FakeApiClient,
                        )

    clock_values = iter([100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0])

    monkeypatch.setattr(
                        time,
                        "monotonic",
                        lambda: next(clock_values),
                    )

    worker = Worker(queue, ApiClient(), 2.0)   

    response = worker.run_once()

    assert response is expected_response
    assert calls == [
                        ("/test", {"timeout": 2.0, "headers": {}})
                    ]
    
@pytest.mark.distributed_lab
def test_worker_timeout_limited_by_job_deadline(monkeypatch):
    
    queue = InMemoryQueue()
    queue.put(Job(
        method="GET",
        path="/test",
        timeout=5.0,
        deadline_s=2.0,
    ))

    expected_response = httpx.Response(200)
    calls = []

    class FakeApiClient:
        def get(self, path, **kwargs):
            calls.append((path, kwargs))
            return expected_response

    monkeypatch.setattr(
                            sys.modules[__name__],
                            "ApiClient",
                            FakeApiClient,
                        )

    clock_values = iter([100.0, 100.0, 100.0, 100.0])

    monkeypatch.setattr(
                        time,
                        "monotonic",
                        lambda: next(clock_values),
                    )

    worker = Worker(queue, ApiClient())   

    response = worker.run_once()

    assert response is expected_response
    assert calls == [
                        ("/test", {"timeout": 2.0, "headers": {}})
                    ]

@pytest.mark.distributed_lab
def test_worker_timeout_limited_by_both_deadlines(monkeypatch):

    queue = InMemoryQueue()
    queue.put(Job(
        method="GET",
        path="/test",
        timeout=5.0,
        deadline_s=4.0,
    ))

    expected_response = httpx.Response(200)
    calls = []

    class FakeApiClient:
        def get(self, path, **kwargs):
            calls.append((path, kwargs))
            return expected_response

    monkeypatch.setattr(
                            sys.modules[__name__],
                            "ApiClient",
                            FakeApiClient,
                        )

    clock_values = iter([100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0])

    monkeypatch.setattr(
                        time,
                        "monotonic",
                        lambda: next(clock_values),
                    )

    worker = Worker(queue, ApiClient(), 2.0)   

    response = worker.run_once()

    assert response is expected_response
    assert calls == [("/test", {"timeout": 2.0, "headers": {}})]

@pytest.mark.distributed_lab
def test_worker_raises_when_worker_deadline_expired_before_request(monkeypatch):

    queue = InMemoryQueue()
    job = Job(
        method="GET",
        path="/test",
        timeout=5.0,
        deadline_s=4.0,
    )
    queue.put(job)

    expected_response = httpx.Response(200)
    calls = []
    call = 0
    class FakeApiClient:
        def get(self, path, **kwargs):
            nonlocal call
            call += 1
            calls.append((path, kwargs))
            return expected_response

    monkeypatch.setattr(
                            sys.modules[__name__],
                            "ApiClient",
                            FakeApiClient,
                        )

    clock_values = iter([100.0, 105.0, 105.0, 105.0, 105.0, 105.0, 105.0])

    monkeypatch.setattr(
                        time,
                        "monotonic",
                        lambda: next(clock_values),
                    )

    worker = Worker(queue, ApiClient(), 2.0)   

    with pytest.raises(WorkerDeadlineExceeded, match="Worker deadline exceeded"):    
        worker.run_once()

    assert call == 0
    assert calls == []
    assert queue.get() is job

@pytest.mark.distributed_lab   
def test_worker_deadline_expires_during_request(monkeypatch):
    
    queue = InMemoryQueue()
    job = Job(
        method="GET",
        path="/test",
        timeout=5.0,
        deadline_s=4.0,
    )
    queue.put(job)

    expected_response = httpx.Response(200)
    calls = []
    call = 0
    class FakeApiClient:
        def get(self, path, **kwargs):
            nonlocal call
            call += 1
            calls.append((path, kwargs))
            return expected_response

    monkeypatch.setattr(
                            sys.modules[__name__],
                            "ApiClient",
                            FakeApiClient,
                        )

    clock_values = iter([100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 103.0])

    monkeypatch.setattr(
                        time,
                        "monotonic",
                        lambda: next(clock_values),
                    )

    worker = Worker(queue, ApiClient(), 2.0)   

    with pytest.raises(WorkerDeadlineExceeded, match="Worker deadline exceeded"):    
        worker.run_once()

    assert call == 1
    assert calls == [("/test", {"timeout": 2.0, "headers": {}})]

@pytest.mark.distributed_lab
def test_worker_deadline_expires_between_retries(monkeypatch):
    
    queue = InMemoryQueue()
    job = Job(
        method="GET",
        path="/test",
        timeout=5.0,
        deadline_s=4.0,
    )
    queue.put(job)

    call = 0
    class FakeApiClient:
        def get(self, path, **kwargs):
            nonlocal call
            call += 1
            request = httpx.Request("GET", "http://example.com/slow")
            cause = httpx.ReadTimeout("Request timed out", request=request)
            raise ApiError("Request failed") from cause


    monkeypatch.setattr(
                            sys.modules[__name__],
                            "ApiClient",
                            FakeApiClient,
                        )

    clock_values = iter([100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 101.0, 101.0, 103.0])

    monkeypatch.setattr(
                        time,
                        "monotonic",
                        lambda: next(clock_values),
                    )

    worker = Worker(queue, ApiClient(), 2.0)   

    with pytest.raises(WorkerDeadlineExceeded, match="Worker deadline exceeded"):    
        worker.run_once()

    assert call == 1

@pytest.mark.distributed_lab
def test_worker_deadline_error_overrides_retry_api_error(
                                                            monkeypatch: pytest.MonkeyPatch,
                                                        ) -> None:
    queue = InMemoryQueue()
    job = Job(
        method="GET",
        path="/test",
        timeout=1.0,
        deadline_s=2.0,
    )
    queue.put(job)

    call = 0
    class FakeApiClient:
        def get(self, path, **kwargs):
            nonlocal call
            call += 1
            request = httpx.Request("GET", "http://example.com/slow")
            cause = httpx.ReadTimeout("Request timed out", request=request)
            raise ApiError("Request failed") from cause


    monkeypatch.setattr(
                            sys.modules[__name__],
                            "ApiClient",
                            FakeApiClient,
                        )

    clock_values = iter([100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 101.0, 101.0, 103.0])

    monkeypatch.setattr(
                        time,
                        "monotonic",
                        lambda: next(clock_values),
                    )

    worker = Worker(queue, ApiClient(), 2.0)   

    with pytest.raises(WorkerDeadlineExceeded, match="Worker deadline exceeded"):    
        worker.run_once()

    assert call == 1


class WorkerTestServer(ThreadingHTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.received_requests = []
        self.lock = Lock()
        self.calls = 0

class WorkerTestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/health":
            body = b"OK"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)

    def idempotency_key(self, headers: dict[str, object] | None) -> dict[str, object] | None:
        if headers is not None:
            key = headers.get("Idempotency-Key")
            if key is not None:
                for n in self.server.received_requests:
                    h = n.get("headers")
                    if h is not None:
                        k = h.get("Idempotency-Key")
                        if k == key:
                            return n
        return None

    def do_POST(self):
        self.server.calls += 1
        received_request = self.idempotency_key(dict(self.headers.items()))
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)
        payload = json.loads(raw_body)
        scheme = getattr(self.server, "scheme", "http")
        host = self.headers.get("Host")
        if not host:
            server_host, server_port = self.server.server_address[:2]
            host = f"{server_host}:{server_port}"
        full_url = f"{scheme}://{host}{self.path}"
        parsed_url = urlsplit(full_url)
        if received_request is None:
            received_request = {
                                    "method": self.command,
                                    "url": full_url,
                                    "scheme": scheme,
                                    "host": host,
                                    "port": parsed_url.port,
                                    "path": self.path,
                                    "url_path": parsed_url.path,
                                    "query": parsed_url.query,
                                    "http_version": self.request_version,
                                    "headers": dict(self.headers.items()),
                                    "client_address": {
                                        "host": self.client_address[0],
                                        "port": self.client_address[1],
                                    },
                                    "server_address": {
                                        "host": self.server.server_address[0],
                                        "port": self.server.server_address[1],
                                    },
                                    "payload": payload,
                                    "raw_body": raw_body,
                                }
            
            with self.server.lock:
                self.server.received_requests.append(received_request)
        
        response_data = {
                            "items": [3, 4],
                            "request": {
                                "method": received_request["method"],
                                "url": received_request["url"],
                                "scheme": received_request["scheme"],
                                "host": received_request["host"],
                                "port": received_request["port"],
                                "path": received_request["path"],
                                "url_path": received_request["url_path"],
                                "query": received_request["query"],
                                "http_version": received_request["http_version"],
                                "headers": received_request["headers"],
                                "client_address": received_request["client_address"],
                                "server_address": received_request["server_address"],
                                "payload": received_request["payload"],
                                "raw_body": received_request["raw_body"].decode("utf-8"),
                            },
                        }
        

        response_body = json.dumps(
                                        response_data,
                                        separators=(",", ":"),
                                    ).encode("utf-8")
        time.sleep(0.5)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, format, *args):
        pass

@pytest.mark.distributed_lab
def test_worker_sends_headers_idempotency_key_and_json_to_http_server():
    server = WorkerTestServer(("127.0.0.1", 0), WorkerTestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        wait_for_server("127.0.0.1", server.server_port)
        wait_for_http_server(base_url)
        client = None
    
        client = ApiClient(
            Settings(
                base_url=base_url,
                timeout_s=1,
                log_level="INFO",
            )
        )

        queue = InMemoryQueue()
        job = Job(
                method="POST",
                path="/test",
                timeout=2.5,
                deadline_s=5.0,
                payload={"name": "John", "id": 10},
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": "Bearer demo-token",
                    "X-Request-ID": "req-123",
                },
                idempotency_key="x101x2555200",
            )
        queue.put(job)
        
        worker = Worker(queue, client)
        assert "idempotency-key" not in worker._queue._queue[0].headers
        assert "Idempotency-Key" not in job.headers
        response = worker.run_once()
        assert response is not None
        assert isinstance(response, httpx.Response)
        assert response.status_code == 200
        assert response.is_success
        assert not response.is_error
        assert not response.is_redirect
        assert response.text
        assert response.reason_phrase == "OK"
        assert response.http_version == "HTTP/1.0"
        expected_items = [3, 4]
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert response_data["items"] == expected_items
        assert response.json()["items"] == [3, 4]
        
        assert response.json() == {
                                    'items': [3, 4], 
                                    'request': 
                                                {
                                       'method': 'POST', 
                                       'url': f'http://127.0.0.1:{server.server_port}/test', 
                                       'scheme': 'http', 
                                       'host': f'127.0.0.1:{server.server_port}', 
                                       'port': server.server_port, 
                                       'path': '/test', 
                                       'url_path': '/test', 
                                       'query': '', 
                                       'http_version': 'HTTP/1.1', 
                                       'headers': {
                                                    'Host': f'127.0.0.1:{server.server_port}', 
                                                   'Accept-Encoding': 'gzip, deflate',
                                                    'Connection': 'keep-alive', 
                                                    'User-Agent': 'python-httpx/0.28.1', 
                                                    'Content-Type': 'application/json', 
                                                    'Accept': 'application/json', 
                                                    'Authorization': 'Bearer demo-token', 
                                                    'X-Request-ID': 'req-123', 
                                                    'Idempotency-Key': 'x101x2555200', 
                                                    'Content-Length': '23'
                                                    }, 
                                        'client_address': {
                                                    'host': '127.0.0.1', 
                                                    'port': server.received_requests[0]["client_address"]["port"]}, 
                                                    'server_address': 
                                                                {
                                                                    'host': '127.0.0.1', 
                                                                    'port': server.server_port
                                                                    }, 
                                                    'payload': 
                                                            {
                                                                'name': 'John', 
                                                                'id': 10
                                                                }, 
                                                    'raw_body': '{"name":"John","id":10}'
                                                }
                                    }
        assert response.content
        assert response.text
        assert response.content == response.text.encode("utf-8")
        assert json.loads(response.content) == response_data
        assert json.loads(response.text) == response_data
        assert response.headers["content-type"] == "application/json"
        assert response.headers["content-type"] == "application/json"
        assert int(response.headers["content-length"]) == len(response.content)
        assert int(response.headers["content-length"]) == len(
                                                                    response.text.encode("utf-8")
                                                                )
        assert response.request is not None
        assert isinstance(response.request, httpx.Request)
        
        assert response.request.method == "POST"
        assert str(response.request.url) == base_url + "/test"
        assert response.request.url == httpx.URL(base_url + "/test")
        assert response.request.url.path == "/test"
        assert response.request.url.scheme == "http"
        assert response.request.url.host == "127.0.0.1"
        assert response.request.url.port == server.server_port
        assert response.request.url.path == "/test"
        assert str(response.request.url) == f"http://127.0.0.1:{server.server_port}/test"
        assert response.request.url.query == b""
        assert response.request.url.fragment == ""
        assert response.request.url.raw_path == b"/test"
        assert response.request.url.is_absolute_url

        assert response.request.extensions["timeout"]["read"] == 2.5
        assert response.request.extensions["timeout"] == {
                                                            "connect": 2.5,
                                                            "read": 2.5,
                                                            "write": 2.5,
                                                            "pool": 2.5,
                                                        }
        assert response.request.extensions["timeout"]["connect"] == 2.5
        assert response.request.extensions["timeout"]["read"] == 2.5
        assert response.request.extensions["timeout"]["write"] == 2.5
        assert response.request.extensions["timeout"]["pool"] == 2.5

        expected_payload = {"name": "John", "id": 10}
        expected_raw_body = b'{"name":"John","id":10}'
        assert response.request.content
        assert response.request.content == expected_raw_body
        assert response.request.read() == expected_raw_body
        assert response.request.content == expected_raw_body
        assert json.loads(response.request.content) == expected_payload
        assert json.loads(response.request.read()) == expected_payload
        assert json.loads(response.request.content) == {"name": "John", "id": 10}
        assert response.request.headers["host"] == f"127.0.0.1:{server.server_port}"
        assert response.request.headers["content-type"] == "application/json"
        assert response.request.headers["content-length"] == str(len(expected_raw_body))
        assert response.request.headers["accept"] == "application/json"
        assert response.request.headers["authorization"] == "Bearer demo-token"
        assert response.request.headers["x-request-id"] == "req-123"
        assert response.request.headers["idempotency-key"] == "x101x2555200"
        assert len(server.received_requests) == 1
        received = server.received_requests[0]
        assert isinstance(received, dict)
        assert received["method"] == "POST"
        assert received["path"] == "/test"
        assert received["url"] == base_url + "/test"
        assert received["scheme"] == "http"
        assert received["host"] == f"127.0.0.1:{server.server_port}"
        assert received["port"] == server.server_port
        assert received["url_path"] == "/test"
        assert received["query"] == ""
        assert received["http_version"] == "HTTP/1.1"
        assert received["payload"] == expected_payload
        assert received["raw_body"] == expected_raw_body
        assert json.loads(received["raw_body"]) == expected_payload
        assert json.loads(received["raw_body"].decode("utf-8")) == expected_payload
        assert received["client_address"]["host"] == "127.0.0.1"
        assert isinstance(received["client_address"]["port"], int)
        assert 0 < received["client_address"]["port"] <= 65535
        assert received["server_address"]["host"] == "127.0.0.1"
        assert received["server_address"]["port"] == server.server_port
        received_headers = {
                                name.lower(): value
                                for name, value in received["headers"].items()
                            }
        assert received_headers["host"] == f"127.0.0.1:{server.server_port}"
        assert received_headers["content-type"] == "application/json"
        assert received_headers["content-length"] == str(len(expected_raw_body))
        assert received_headers["accept"] == "application/json"
        assert received_headers["authorization"] == "Bearer demo-token"
        assert received_headers["x-request-id"] == "req-123"
        assert received_headers["idempotency-key"] == "x101x2555200"
        response_request = response_data["request"]
        assert response_request["method"] == received["method"]
        assert response_request["url"] == received["url"]
        assert response_request["scheme"] == received["scheme"]
        assert response_request["host"] == received["host"]
        assert response_request["port"] == received["port"]
        assert response_request["path"] == received["path"]
        assert response_request["url_path"] == received["url_path"]
        assert response_request["query"] == received["query"]
        assert response_request["http_version"] == received["http_version"]
        assert response_request["headers"] == received["headers"]
        assert response_request["client_address"] == received["client_address"]
        assert response_request["server_address"] == received["server_address"]
        assert response_request["payload"] == received["payload"]
        assert response_request["raw_body"] == received["raw_body"].decode("utf-8")
        assert response_data["items"] == [3, 4]
        assert response_request["payload"] == expected_payload
        assert json.loads(response_request["raw_body"]) == expected_payload
        assert response_request["payload"] == {'name': 'John', 'id': 10}
        assert job.payload == expected_payload
        assert job.headers["Content-Type"] == "application/json"
        assert job.headers["Accept"] == "application/json"
        assert job.headers["Authorization"] == "Bearer demo-token"
        assert job.headers["X-Request-ID"] == "req-123"
        assert job.idempotency_key == "x101x2555200"
        assert "Idempotency-Key" not in job.headers
        assert "idempotency-key" not in job.headers
        assert queue.get() is None
        assert queue.get() is None
        expected_response_body = json.dumps(
                                                response_data,
                                                separators=(",", ":"),
                                            ).encode("utf-8")

        assert response.content == expected_response_body
        assert response.text == expected_response_body.decode("utf-8")
        assert response.headers["content-type"] == "application/json"

    finally:
        if client is not None:
            client.close()
        
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

@pytest.mark.distributed_lab
def test_worker_does_not_send_idempotency_key_when_not_configured():
    # Verify that Worker does not add Idempotency-Key when the job has no key.
    server = WorkerTestServer(("127.0.0.1", 0), WorkerTestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        wait_for_server("127.0.0.1", server.server_port)
        wait_for_http_server(base_url)
        client = None
    
        client = ApiClient(
            Settings(
                base_url=base_url,
                timeout_s=1,
                log_level="INFO",
            )
        )

        queue = InMemoryQueue()
        job = Job(
                method="POST",
                path="/test",
                timeout=2.5,
                deadline_s=5.0,
                payload={"name": "John", "id": 10},
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": "Bearer demo-token",
                    "X-Request-ID": "req-123",
                },
                
            )
        queue.put(job)
        worker = Worker(queue, client)
        assert job.idempotency_key is None
        assert "Idempotency-Key" not in job.headers
        assert queue._queue[0].idempotency_key is None
        assert "idempotency-key" not in queue._queue[0].headers
        assert worker._queue._queue[0].idempotency_key is None
        assert "idempotency-key" not in worker._queue._queue[0].headers
        response = worker.run_once()
        assert response is not None
        assert isinstance(response, httpx.Response)
        assert response.status_code == 200
        assert response.is_success
        assert not response.is_error
        assert not response.is_redirect
        assert response.text
        assert response.reason_phrase == "OK"
        assert response.http_version == "HTTP/1.0"
        expected_items = [3, 4]
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert response_data["items"] == expected_items
        assert response.json()["items"] == [3, 4]
        
        assert response.json() == {
                                    'items': [3, 4], 
                                    'request': 
                                                {
                                       'method': 'POST', 
                                       'url': f'http://127.0.0.1:{server.server_port}/test', 
                                       'scheme': 'http', 
                                       'host': f'127.0.0.1:{server.server_port}', 
                                       'port': server.server_port, 
                                       'path': '/test', 
                                       'url_path': '/test', 
                                       'query': '', 
                                       'http_version': 'HTTP/1.1', 
                                       'headers': {
                                                    'Host': f'127.0.0.1:{server.server_port}', 
                                                   'Accept-Encoding': 'gzip, deflate',
                                                    'Connection': 'keep-alive', 
                                                    'User-Agent': 'python-httpx/0.28.1', 
                                                    'Content-Type': 'application/json', 
                                                    'Accept': 'application/json', 
                                                    'Authorization': 'Bearer demo-token', 
                                                    'X-Request-ID': 'req-123',  
                                                    'Content-Length': '23'
                                                    }, 
                                        'client_address': {
                                                    'host': '127.0.0.1', 
                                                    'port': server.received_requests[0]["client_address"]["port"]}, 
                                                    'server_address': 
                                                                {
                                                                    'host': '127.0.0.1', 
                                                                    'port': server.server_port
                                                                    }, 
                                                    'payload': 
                                                            {
                                                                'name': 'John', 
                                                                'id': 10
                                                                }, 
                                                    'raw_body': '{"name":"John","id":10}'
                                                }
                                    }
        assert response.content
        assert response.text
        assert response.content == response.text.encode("utf-8")
        assert json.loads(response.content) == response_data
        assert json.loads(response.text) == response_data
        assert response.headers["content-type"] == "application/json"
        assert response.headers["content-type"] == "application/json"
        assert int(response.headers["content-length"]) == len(response.content)
        assert int(response.headers["content-length"]) == len(
                                                                    response.text.encode("utf-8")
                                                                )
        assert response.request is not None
        assert isinstance(response.request, httpx.Request)
        
        assert response.request.method == "POST"
        assert str(response.request.url) == base_url + "/test"
        assert response.request.url == httpx.URL(base_url + "/test")
        assert response.request.url.path == "/test"
        assert response.request.url.scheme == "http"
        assert response.request.url.host == "127.0.0.1"
        assert response.request.url.port == server.server_port
        assert response.request.url.path == "/test"
        assert str(response.request.url) == f"http://127.0.0.1:{server.server_port}/test"
        assert response.request.url.query == b""
        assert response.request.url.fragment == ""
        assert response.request.url.raw_path == b"/test"
        assert response.request.url.is_absolute_url

        assert response.request.extensions["timeout"]["read"] == 2.5
        assert response.request.extensions["timeout"] == {
                                                            "connect": 2.5,
                                                            "read": 2.5,
                                                            "write": 2.5,
                                                            "pool": 2.5,
                                                        }
        assert response.request.extensions["timeout"]["connect"] == 2.5
        assert response.request.extensions["timeout"]["read"] == 2.5
        assert response.request.extensions["timeout"]["write"] == 2.5
        assert response.request.extensions["timeout"]["pool"] == 2.5

        expected_payload = {"name": "John", "id": 10}
        expected_raw_body = b'{"name":"John","id":10}'
        assert response.request.content
        assert response.request.content == expected_raw_body
        assert response.request.read() == expected_raw_body
        assert response.request.content == expected_raw_body
        assert json.loads(response.request.content) == expected_payload
        assert json.loads(response.request.read()) == expected_payload
        assert json.loads(response.request.content) == {"name": "John", "id": 10}
        assert response.request.headers["host"] == f"127.0.0.1:{server.server_port}"
        assert response.request.headers["content-type"] == "application/json"
        assert response.request.headers["content-length"] == str(len(expected_raw_body))
        assert response.request.headers["accept"] == "application/json"
        assert response.request.headers["authorization"] == "Bearer demo-token"
        assert response.request.headers["x-request-id"] == "req-123"
        assert "idempotency-key" not in response.request.headers
        assert len(server.received_requests) == 1
        received = server.received_requests[0]
        assert isinstance(received, dict)
        assert received["method"] == "POST"
        assert received["path"] == "/test"
        assert received["url"] == base_url + "/test"
        assert received["scheme"] == "http"
        assert received["host"] == f"127.0.0.1:{server.server_port}"
        assert received["port"] == server.server_port
        assert received["url_path"] == "/test"
        assert received["query"] == ""
        assert received["http_version"] == "HTTP/1.1"
        assert received["payload"] == expected_payload
        assert received["raw_body"] == expected_raw_body
        assert json.loads(received["raw_body"]) == expected_payload
        assert json.loads(received["raw_body"].decode("utf-8")) == expected_payload
        assert received["client_address"]["host"] == "127.0.0.1"
        assert isinstance(received["client_address"]["port"], int)
        assert 0 < received["client_address"]["port"] <= 65535
        assert received["server_address"]["host"] == "127.0.0.1"
        assert received["server_address"]["port"] == server.server_port
        received_headers = {
                                name.lower(): value
                                for name, value in received["headers"].items()
                            }
        assert received_headers["host"] == f"127.0.0.1:{server.server_port}"
        assert received_headers["content-type"] == "application/json"
        assert received_headers["content-length"] == str(len(expected_raw_body))
        assert received_headers["accept"] == "application/json"
        assert received_headers["authorization"] == "Bearer demo-token"
        assert received_headers["x-request-id"] == "req-123"
        assert "idempotency-key" not in received_headers
        response_request = response_data["request"]
        assert response_request["method"] == received["method"]
        assert response_request["url"] == received["url"]
        assert response_request["scheme"] == received["scheme"]
        assert response_request["host"] == received["host"]
        assert response_request["port"] == received["port"]
        assert response_request["path"] == received["path"]
        assert response_request["url_path"] == received["url_path"]
        assert response_request["query"] == received["query"]
        assert response_request["http_version"] == received["http_version"]
        assert response_request["headers"] == received["headers"]
        assert response_request["client_address"] == received["client_address"]
        assert response_request["server_address"] == received["server_address"]
        assert response_request["payload"] == received["payload"]
        assert response_request["raw_body"] == received["raw_body"].decode("utf-8")
        assert response_data["items"] == [3, 4]
        assert response_request["payload"] == expected_payload
        assert json.loads(response_request["raw_body"]) == expected_payload
        assert response_request["payload"] == {'name': 'John', 'id': 10}
        assert job.payload == expected_payload
        assert job.headers["Content-Type"] == "application/json"
        assert job.headers["Accept"] == "application/json"
        assert job.headers["Authorization"] == "Bearer demo-token"
        assert job.headers["X-Request-ID"] == "req-123"
        
        assert "Idempotency-Key" not in job.headers
        assert "idempotency-key" not in job.headers
        assert queue.get() is None
        assert queue.get() is None
        expected_response_body = json.dumps(
                                                response_data,
                                                separators=(",", ":"),
                                            ).encode("utf-8")

        assert response.content == expected_response_body
        assert response.text == expected_response_body.decode("utf-8")
        assert response.headers["content-type"] == "application/json"

    finally:
        if client is not None:
            client.close()
        
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)



@pytest.mark.distributed_lab
def test_worker_does_not_retry_post_after_timeout():
    # Verify that Worker sends the same Idempotency-Key on every retry.
    server = WorkerTestServer(("127.0.0.1", 0), WorkerTestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        wait_for_server("127.0.0.1", server.server_port)
        wait_for_http_server(base_url)
        client = None
    
        client = ApiClient(
            Settings(
                base_url=base_url,
                timeout_s=1,
                log_level="INFO",
            )
        )

        queue = InMemoryQueue()
        job = Job(
                method="POST",
                path="/test",
                timeout=0.3,
                deadline_s=0.7,
                payload={"name": "John", "id": 10},
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": "Bearer demo-token",
                    "X-Request-ID": "req-123",
                },
                idempotency_key="x101x2555200",
            )
        queue.put(job)
        response = None
        worker = Worker(queue, client)
        assert "idempotency-key" not in worker._queue._queue[0].headers
        assert "Idempotency-Key" not in job.headers
        with pytest.raises(ApiError, match="POST /test failed: timed out") as exc_info:
            response = worker.run_once()
        assert exc_info.type is ApiError
        assert str(exc_info.value) == "POST /test failed: timed out"
        assert "POST /test" in str(exc_info.value)
        assert "timed out" in str(exc_info.value)
        assert re.search(r"POST /test failed: timed out", str(exc_info.value))
        assert exc_info.type is ApiError
        assert isinstance(exc_info.value, ApiError)
        assert type(exc_info.value) is ApiError
        assert type(exc_info.value).__name__ == "ApiError"
        
        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, httpx.TimeoutException)
        assert isinstance(exc_info.value.__cause__,  httpx.ReadTimeout)
        
        assert len(exc_info.value.args) == 1
        assert isinstance(exc_info.value.args[0], str)
        assert "timed out" in exc_info.value.args[0]
        assert str(exc_info.value) == "POST /test failed: timed out"
        assert "POST /test" in str(exc_info.value)
        assert "timed out" in str(exc_info.value)
        assert str(exc_info.value).startswith("POST /test failed:")
        assert str(exc_info.value).endswith("timed out")
        assert re.search(r"POST /test failed: timed out", str(exc_info.value))
        assert exc_info.value.args == ("POST /test failed: timed out",)
        
        assert exc_info.type is ApiError
        assert isinstance(exc_info.value, ApiError)
        assert type(exc_info.value).__name__ == "ApiError"
        assert str(exc_info.value).startswith("POST /test failed:")
        assert str(exc_info.value).endswith("timed out")
        assert str(exc_info.value) == str(exc_info.value)
        assert repr(exc_info.value)
        assert exc_info.value.__cause__ is not None
        assert type(exc_info.value.__cause__) is httpx.ReadTimeout
        assert isinstance(exc_info.value.__cause__, Exception)
        assert "timed out" in str(exc_info.value.__cause__).lower()
        assert (
                    exc_info.value.__context__ is None
                    or isinstance(exc_info.value.__context__, Exception)
                )
        assert exc_info.tb is not None
        assert exc_info.traceback is not None
        assert exc_info.traceback[-1].name == "_request"
        cause = exc_info.value.__cause__
        assert cause is not None
        assert isinstance(cause, Exception)
        assert isinstance(cause, httpx.HTTPError)
        assert isinstance(cause, httpx.TimeoutException)
        assert isinstance(cause, httpx.ReadTimeout)

        assert type(cause) is httpx.ReadTimeout
        assert type(cause).__name__ == "ReadTimeout"
        assert str(cause)
        assert isinstance(str(cause), str)
        assert "timed out" in str(cause).lower()
        assert str(cause) == str(cause)
        assert repr(cause)
        assert type(cause).__name__ in repr(cause)
        assert isinstance(cause.args, tuple)
        assert len(cause.args) >= 0
        assert all(isinstance(arg, object) for arg in cause.args)
        assert str(cause) != ""
        assert str(cause) in str(exc_info.value)
        assert cause.request is not None
        assert cause.request.method == "POST"
        assert cause.request.url.path == "/test"
        assert str(cause.request.url) == base_url + "/test"
        assert cause.request.url.scheme == "http"
        assert cause.request.url.port == server.server_port
        assert exc_info.value.__cause__ is cause
        assert exc_info.value.__context__ is cause
        assert exc_info.value.__suppress_context__ is True
        assert exc_info.value.__context__ is not None
        assert isinstance(exc_info.value.__context__, Exception)
        assert type(exc_info.value.__context__) is type(cause)
        assert str(exc_info.value.__context__) == str(cause)
        assert exc_info.type is ApiError
        assert exc_info.value is not None
        assert exc_info.typename == "ApiError"
        assert exc_info.tb is not None
        assert exc_info.traceback is not None
        assert len(exc_info.traceback) > 0
        frame_names = [frame.name for frame in exc_info.traceback]

        assert "run_once" in frame_names
        assert "_request" in frame_names
        assert "execute" in frame_names
        assert exc_info.traceback[-1].name == "_request"
        assert "ApiError" in exc_info.exconly()
        assert "POST /test failed:" in exc_info.exconly()
        error = exc_info.value
        cause = error.__cause__

        assert type(error) is ApiError
        assert str(error).startswith("POST /test failed:")
        assert cause is not None
        assert isinstance(cause, httpx.ReadTimeout)
        assert error.__context__ is cause
        assert error.__suppress_context__ is True
        assert cause.request.method == "POST"
        assert cause.request.url.path == "/test"
        
        assert error.__traceback__ is not None
        assert cause.__traceback__ is not None
        assert isinstance(error.__traceback__, type(exc_info.tb))

        error = exc_info.value
        cause = error.__cause__

        # Verify the wrapped exception.
        assert exc_info.type is ApiError
        assert str(error) == "POST /test failed: timed out"

        # Verify the original cause.
        assert cause is not None
        assert isinstance(cause, httpx.ReadTimeout)
        assert "timed out" in str(cause).lower()

        # Verify exception chaining.
        assert error.__context__ is cause
        assert error.__suppress_context__ is True

        # Verify the request associated with the cause.
        assert cause.request.method == "POST"
        assert cause.request.url.path == "/test"

        # Verify traceback.
        assert exc_info.tb is not None
        assert "run_once" in [frame.name for frame in exc_info.traceback]


        assert response is None
        assert server.calls == 1
        assert len(server.received_requests) == 1
        received = server.received_requests[0]
        assert isinstance(received, dict)
        assert received["method"] == "POST"
        assert received["path"] == "/test"
        assert received["url"] == base_url + "/test"
        assert received["scheme"] == "http"
        assert received["host"] == f"127.0.0.1:{server.server_port}"
        assert received["port"] == server.server_port
        assert received["url_path"] == "/test"
        assert received["query"] == ""
        assert received["http_version"] == "HTTP/1.1"
        assert received["client_address"]["host"] == "127.0.0.1"
        assert isinstance(received["client_address"]["port"], int)
        assert 0 < received["client_address"]["port"] <= 65535
        assert received["server_address"]["host"] == "127.0.0.1"
        assert received["server_address"]["port"] == server.server_port
        received_headers = {
                                name.lower(): value
                                for name, value in received["headers"].items()
                            }
        assert received_headers["host"] == f"127.0.0.1:{server.server_port}"
        assert received_headers["content-type"] == "application/json"
        assert received_headers["accept"] == "application/json"
        assert received_headers["authorization"] == "Bearer demo-token"
        assert received_headers["x-request-id"] == "req-123"
        assert received_headers["idempotency-key"] == "x101x2555200"
        assert job.headers["Content-Type"] == "application/json"
        assert job.headers["Accept"] == "application/json"
        assert job.headers["Authorization"] == "Bearer demo-token"
        assert job.headers["X-Request-ID"] == "req-123"
        assert job.idempotency_key == "x101x2555200"
        assert "Idempotency-Key" not in job.headers
        assert "idempotency-key" not in job.headers
        assert queue.get() is None
        assert queue.get() is None
        

    finally:
        if client is not None:
            client.close()
        
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)



@pytest.mark.distributed_lab
def test_server_reuses_first_request_for_same_idempotency_key():
    # Verify that Worker sends the same Idempotency-Key on every retry.
    server = WorkerTestServer(("127.0.0.1", 0), WorkerTestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        wait_for_server("127.0.0.1", server.server_port)
        wait_for_http_server(base_url)
        client = None
    
        client = ApiClient(
            Settings(
                base_url=base_url,
                timeout_s=1,
                log_level="INFO",
            )
        )

        queue = InMemoryQueue()
        job1 = Job(
                method="POST",
                path="/test",
                timeout=1,
                deadline_s=2,
                payload={"name": "John", "id": 10},
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": "Bearer demo-token",
                    "X-Request-ID": "req-123",
                },
                idempotency_key="x101x2555200",
            )

        job2 = Job(
                        method="POST",
                        path="/test2",
                        timeout=1,
                        deadline_s=2,
                        payload={"name": "Anna", "id": 23},
                        headers={
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                            "Authorization": "Bearer demo-token_2",
                            "X-Request-ID": "req-123",
                        },
                        idempotency_key="x101x2555200",
                    )
        
        queue.put(job1)
        queue.put(job2)
        
        worker = Worker(queue, client)
        response = worker.run_once()

        assert response is not None
        assert server.calls == 1
        assert len(server.received_requests) == 1

        assert isinstance(response, httpx.Response)
        assert response.status_code == 200
        assert response.is_success
        assert not response.is_error
        assert not response.is_redirect
        assert response.text
        assert response.reason_phrase == "OK"
        assert response.http_version == "HTTP/1.0"
        expected_items = [3, 4]
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert response_data["items"] == expected_items
        assert response.json()["items"] == [3, 4]
        
        assert response.json() == {
                                    'items': [3, 4], 
                                    'request': 
                                                {
                                       'method': 'POST', 
                                       'url': f'http://127.0.0.1:{server.server_port}/test', 
                                       'scheme': 'http', 
                                       'host': f'127.0.0.1:{server.server_port}', 
                                       'port': server.server_port, 
                                       'path': '/test', 
                                       'url_path': '/test', 
                                       'query': '', 
                                       'http_version': 'HTTP/1.1', 
                                       'headers': {
                                                    'Host': f'127.0.0.1:{server.server_port}', 
                                                   'Accept-Encoding': 'gzip, deflate',
                                                    'Connection': 'keep-alive', 
                                                    'User-Agent': 'python-httpx/0.28.1', 
                                                    'Content-Type': 'application/json', 
                                                    'Accept': 'application/json', 
                                                    'Authorization': 'Bearer demo-token', 
                                                    'X-Request-ID': 'req-123', 
                                                    'Idempotency-Key': 'x101x2555200', 
                                                    'Content-Length': '23'
                                                    }, 
                                        'client_address': {
                                                    'host': '127.0.0.1', 
                                                    'port': server.received_requests[0]["client_address"]["port"]}, 
                                                    'server_address': 
                                                                {
                                                                    'host': '127.0.0.1', 
                                                                    'port': server.server_port
                                                                    }, 
                                                    'payload': 
                                                            {
                                                                'name': 'John', 
                                                                'id': 10
                                                                }, 
                                                    'raw_body': '{"name":"John","id":10}'
                                                }
                                    }
        assert response.content
        assert response.text
        assert response.content == response.text.encode("utf-8")
        assert json.loads(response.content) == response_data
        assert json.loads(response.text) == response_data
        assert response.headers["content-type"] == "application/json"
        assert response.headers["content-type"] == "application/json"
        assert int(response.headers["content-length"]) == len(response.content)
        assert int(response.headers["content-length"]) == len(
                                                                    response.text.encode("utf-8")
                                                                )
        assert response.request is not None
        assert isinstance(response.request, httpx.Request)
        
        assert response.request.method == "POST"
        assert str(response.request.url) == base_url + "/test"
        assert response.request.url == httpx.URL(base_url + "/test")
        assert response.request.url.path == "/test"
        assert response.request.url.scheme == "http"
        assert response.request.url.host == "127.0.0.1"
        assert response.request.url.port == server.server_port
        assert response.request.url.path == "/test"
        assert str(response.request.url) == f"http://127.0.0.1:{server.server_port}/test"
        assert response.request.url.query == b""
        assert response.request.url.fragment == ""
        assert response.request.url.raw_path == b"/test"
        assert response.request.url.is_absolute_url

        assert response.request.extensions["timeout"]["read"] == 1.0
        assert response.request.extensions["timeout"] == {
                                                            "connect": 1.0,
                                                            "read": 1.0,
                                                            "write": 1.0,
                                                            "pool": 1.0,
                                                        }
        assert response.request.extensions["timeout"]["connect"] == 1.0
        assert response.request.extensions["timeout"]["read"] == 1.0
        assert response.request.extensions["timeout"]["write"] == 1.0
        assert response.request.extensions["timeout"]["pool"] == 1.0

        expected_payload = {"name": "John", "id": 10}
        expected_raw_body = b'{"name":"John","id":10}'
        assert response.request.content
        assert response.request.content == expected_raw_body
        assert response.request.read() == expected_raw_body
        assert response.request.content == expected_raw_body
        assert json.loads(response.request.content) == expected_payload
        assert json.loads(response.request.read()) == expected_payload
        assert json.loads(response.request.content) == {"name": "John", "id": 10}
        assert response.request.headers["host"] == f"127.0.0.1:{server.server_port}"
        assert response.request.headers["content-type"] == "application/json"
        assert response.request.headers["content-length"] == str(len(expected_raw_body))
        assert response.request.headers["accept"] == "application/json"
        assert response.request.headers["authorization"] == "Bearer demo-token"
        assert response.request.headers["x-request-id"] == "req-123"
        assert response.request.headers["idempotency-key"] == "x101x2555200"
        assert len(server.received_requests) == 1
        received = server.received_requests[0]
        assert isinstance(received, dict)
        assert received["method"] == "POST"
        assert received["path"] == "/test"
        assert received["url"] == base_url + "/test"
        assert received["scheme"] == "http"
        assert received["host"] == f"127.0.0.1:{server.server_port}"
        assert received["port"] == server.server_port
        assert received["url_path"] == "/test"
        assert received["query"] == ""
        assert received["http_version"] == "HTTP/1.1"
        assert received["payload"] == expected_payload
        assert received["raw_body"] == expected_raw_body
        assert json.loads(received["raw_body"]) == expected_payload
        assert json.loads(received["raw_body"].decode("utf-8")) == expected_payload
        assert received["client_address"]["host"] == "127.0.0.1"
        assert isinstance(received["client_address"]["port"], int)
        assert 0 < received["client_address"]["port"] <= 65535
        assert received["server_address"]["host"] == "127.0.0.1"
        assert received["server_address"]["port"] == server.server_port
        received_headers = {
                                name.lower(): value
                                for name, value in received["headers"].items()
                            }
        assert received_headers["host"] == f"127.0.0.1:{server.server_port}"
        assert received_headers["content-type"] == "application/json"
        assert received_headers["content-length"] == str(len(expected_raw_body))
        assert received_headers["accept"] == "application/json"
        assert received_headers["authorization"] == "Bearer demo-token"
        assert received_headers["x-request-id"] == "req-123"
        assert received_headers["idempotency-key"] == "x101x2555200"
        response_request = response_data["request"]
        assert response_request["method"] == received["method"]
        assert response_request["url"] == received["url"]
        assert response_request["scheme"] == received["scheme"]
        assert response_request["host"] == received["host"]
        assert response_request["port"] == received["port"]
        assert response_request["path"] == received["path"]
        assert response_request["url_path"] == received["url_path"]
        assert response_request["query"] == received["query"]
        assert response_request["http_version"] == received["http_version"]
        assert response_request["headers"] == received["headers"]
        assert response_request["client_address"] == received["client_address"]
        assert response_request["server_address"] == received["server_address"]
        assert response_request["payload"] == received["payload"]
        assert response_request["raw_body"] == received["raw_body"].decode("utf-8")
        assert response_data["items"] == [3, 4]
        assert response_request["payload"] == expected_payload
        assert json.loads(response_request["raw_body"]) == expected_payload
        assert response_request["payload"] == {'name': 'John', 'id': 10}
        assert job1.payload == expected_payload
        assert job1.headers["Content-Type"] == "application/json"
        assert job1.headers["Accept"] == "application/json"
        assert job1.headers["Authorization"] == "Bearer demo-token"
        assert job1.headers["X-Request-ID"] == "req-123"
        assert job1.idempotency_key == "x101x2555200"
        assert "Idempotency-Key" not in job1.headers
        assert "idempotency-key" not in job1.headers
    
        expected_response_body = json.dumps(
                                                response_data,
                                                separators=(",", ":"),
                                            ).encode("utf-8")

        assert response.content == expected_response_body
        assert response.text == expected_response_body.decode("utf-8")
        assert response.headers["content-type"] == "application/json"       

        response = worker.run_once()
        assert response is not None
        assert server.calls == 2
        assert len(server.received_requests) == 1

        assert isinstance(response, httpx.Response)
        assert response.status_code == 200
        assert response.is_success
        assert not response.is_error
        assert not response.is_redirect
        assert response.text
        assert response.reason_phrase == "OK"
        assert response.http_version == "HTTP/1.0"
        expected_items = [3, 4]
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert response_data["items"] == expected_items
        assert response.json()["items"] == [3, 4]
        
        assert response.json() == {
                                    'items': [3, 4], 
                                    'request': 
                                                {
                                       'method': 'POST', 
                                       'url': f'http://127.0.0.1:{server.server_port}/test', 
                                       'scheme': 'http', 
                                       'host': f'127.0.0.1:{server.server_port}', 
                                       'port': server.server_port, 
                                       'path': '/test', 
                                       'url_path': '/test', 
                                       'query': '', 
                                       'http_version': 'HTTP/1.1', 
                                       'headers': {
                                                    'Host': f'127.0.0.1:{server.server_port}', 
                                                   'Accept-Encoding': 'gzip, deflate',
                                                    'Connection': 'keep-alive', 
                                                    'User-Agent': 'python-httpx/0.28.1', 
                                                    'Content-Type': 'application/json', 
                                                    'Accept': 'application/json', 
                                                    'Authorization': 'Bearer demo-token', 
                                                    'X-Request-ID': 'req-123', 
                                                    'Idempotency-Key': 'x101x2555200', 
                                                    'Content-Length': '23'
                                                    }, 
                                        'client_address': {
                                                    'host': '127.0.0.1', 
                                                    'port': server.received_requests[0]["client_address"]["port"]}, 
                                                    'server_address': 
                                                                {
                                                                    'host': '127.0.0.1', 
                                                                    'port': server.server_port
                                                                    }, 
                                                    'payload': 
                                                            {
                                                                'name': 'John', 
                                                                'id': 10
                                                                }, 
                                                    'raw_body': '{"name":"John","id":10}'
                                                }
                                    }
        assert response.content
        assert response.text
        assert response.content == response.text.encode("utf-8")
        assert json.loads(response.content) == response_data
        assert json.loads(response.text) == response_data
        assert response.headers["content-type"] == "application/json"
        assert response.headers["content-type"] == "application/json"
        assert int(response.headers["content-length"]) == len(response.content)
        assert int(response.headers["content-length"]) == len(
                                                                    response.text.encode("utf-8")
                                                                )
        assert response.request is not None
        assert isinstance(response.request, httpx.Request)
        
        assert response.request.method == "POST"
        assert str(response.request.url) == base_url + "/test2"
        assert response.request.url == httpx.URL(base_url + "/test2")
        assert response.request.url.path == "/test2"
        assert response.request.url.scheme == "http"
        assert response.request.url.host == "127.0.0.1"
        assert response.request.url.port == server.server_port
        assert response.request.url.path == "/test2"
        assert str(response.request.url) == f"http://127.0.0.1:{server.server_port}/test2"
        assert response.request.url.query == b""
        assert response.request.url.fragment == ""
        assert response.request.url.raw_path == b"/test2"
        assert response.request.url.is_absolute_url

        assert response.request.extensions["timeout"]["read"] == 1.0
        assert response.request.extensions["timeout"] == {
                                                            "connect": 1.0,
                                                            "read": 1.0,
                                                            "write": 1.0,
                                                            "pool": 1.0,
                                                        }
        assert response.request.extensions["timeout"]["connect"] == 1.0
        assert response.request.extensions["timeout"]["read"] == 1.0
        assert response.request.extensions["timeout"]["write"] == 1.0
        assert response.request.extensions["timeout"]["pool"] == 1.0

        expected_payload = {"name": "John", "id": 10}
        expected_raw_body = b'{"name":"John","id":10}'
        assert response.request.content
        assert response.request.content == b'{"name":"Anna","id":23}'
        assert response.request.read() == b'{"name":"Anna","id":23}'
        assert response.request.content == b'{"name":"Anna","id":23}'
        assert json.loads(response.request.content) == {'name': 'Anna', 'id': 23}
        assert json.loads(response.request.read()) == {'name': 'Anna', 'id': 23}
        assert json.loads(response.request.content) == {'name': 'Anna', 'id': 23}
        assert response.request.headers["host"] == f"127.0.0.1:{server.server_port}"
        assert response.request.headers["content-type"] == "application/json"
        assert response.request.headers["content-length"] == str(len(expected_raw_body))
        assert response.request.headers["accept"] == "application/json"
        assert response.request.headers["authorization"] == "Bearer demo-token_2"
        assert response.request.headers["x-request-id"] == "req-123"
        assert response.request.headers["idempotency-key"] == "x101x2555200"
        assert len(server.received_requests) == 1
        received = server.received_requests[0]
        assert isinstance(received, dict)
        assert received["method"] == "POST"
        assert received["path"] == "/test"
        assert received["url"] == base_url + "/test"
        assert received["scheme"] == "http"
        assert received["host"] == f"127.0.0.1:{server.server_port}"
        assert received["port"] == server.server_port
        assert received["url_path"] == "/test"
        assert received["query"] == ""
        assert received["http_version"] == "HTTP/1.1"
        assert received["payload"] == expected_payload
        assert received["raw_body"] == expected_raw_body
        assert json.loads(received["raw_body"]) == expected_payload
        assert json.loads(received["raw_body"].decode("utf-8")) == expected_payload
        assert received["client_address"]["host"] == "127.0.0.1"
        assert isinstance(received["client_address"]["port"], int)
        assert 0 < received["client_address"]["port"] <= 65535
        assert received["server_address"]["host"] == "127.0.0.1"
        assert received["server_address"]["port"] == server.server_port
        received_headers = {
                                name.lower(): value
                                for name, value in received["headers"].items()
                            }
        assert received_headers["host"] == f"127.0.0.1:{server.server_port}"
        assert received_headers["content-type"] == "application/json"
        assert received_headers["content-length"] == str(len(expected_raw_body))
        assert received_headers["accept"] == "application/json"
        assert received_headers["authorization"] == "Bearer demo-token"
        assert received_headers["x-request-id"] == "req-123"
        assert received_headers["idempotency-key"] == "x101x2555200"
        response_request = response_data["request"]
        assert response_request["method"] == received["method"]
        assert response_request["url"] == received["url"]
        assert response_request["scheme"] == received["scheme"]
        assert response_request["host"] == received["host"]
        assert response_request["port"] == received["port"]
        assert response_request["path"] == received["path"]
        assert response_request["url_path"] == received["url_path"]
        assert response_request["query"] == received["query"]
        assert response_request["http_version"] == received["http_version"]
        assert response_request["headers"] == received["headers"]
        assert response_request["client_address"] == received["client_address"]
        assert response_request["server_address"] == received["server_address"]
        assert response_request["payload"] == received["payload"]
        assert response_request["raw_body"] == received["raw_body"].decode("utf-8")
        assert response_data["items"] == [3, 4]
        assert response_request["payload"] == expected_payload
        assert json.loads(response_request["raw_body"]) == expected_payload
        assert response_request["payload"] == {'name': 'John', 'id': 10}
        assert job1.payload == expected_payload
        assert job1.headers["Content-Type"] == "application/json"
        assert job1.headers["Accept"] == "application/json"
        assert job1.headers["Authorization"] == "Bearer demo-token"
        assert job1.headers["X-Request-ID"] == "req-123"
        assert job1.idempotency_key == "x101x2555200"
        assert "Idempotency-Key" not in job1.headers
        assert "idempotency-key" not in job1.headers
        
        assert job2.payload == {"name": "Anna", "id": 23}
        assert job2.headers["Content-Type"] == "application/json"
        assert job2.headers["Accept"] == "application/json"
        assert job2.headers["Authorization"] == "Bearer demo-token_2"
        assert job2.headers["X-Request-ID"] == "req-123"
        assert job2.idempotency_key == "x101x2555200"
        assert "Idempotency-Key" not in job2.headers
        assert "idempotency-key" not in job2.headers


        assert queue.get() is None
        assert queue.get() is None
        expected_response_body = json.dumps(
                                                response_data,
                                                separators=(",", ":"),
                                            ).encode("utf-8")

        assert response.content == expected_response_body
        assert response.text == expected_response_body.decode("utf-8")
        assert response.headers["content-type"] == "application/json"       

    
    finally:
        if client is not None:
            client.close()
        
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

@pytest.mark.distributed_lab
def test_worker_preserves_idempotency_key_across_get_retries(settings):
    # Verify that every GET retry sends the same Idempotency-Key.
    
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        assert request.headers["Idempotency-Key"] == "x101x2555200"
        if attempts < 2:
            return httpx.Response(503, request=request)

        return httpx.Response(
            200,
            request=request,
            json={"ok": True},
        )

    transport = httpx.MockTransport(handler)
    
    with ApiClient(settings, transport=transport) as client:
        queue = InMemoryQueue()
        queue.put(Job(
                method="GET",
                path="/users",
                timeout=1,
                deadline_s=2,
                payload={"name": "John", "id": 10},
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": "Bearer demo-token",
                    "X-Request-ID": "req-123",
                },
                idempotency_key="x101x2555200",
            ))
        worker = Worker(queue, client)
        response = worker.run_once()

        assert attempts == 2
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        assert response.request.method == "GET"
        assert response.request.url.path == "/users"
        assert response.request.headers["Idempotency-Key"] == "x101x2555200"

@pytest.mark.distributed_lab
def test_worker_preserves_idempotency_key_across_get_retries_tracks_all_attempts(settings):
    # Verify that every GET retry sends the same Idempotency-Key.

    idempotency_keys = []
    status = []
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        assert request.headers["Idempotency-Key"] == "x101x2555200"
        idempotency_keys.append(request.headers["Idempotency-Key"])
        if attempts < 2:
            status.append(503)
            return httpx.Response(503, request=request)
        status.append(200)
        return httpx.Response(
            200,
            request=request,
            json={"ok": True},
        )

    transport = httpx.MockTransport(handler)
    
    with ApiClient(settings, transport=transport) as client:
        queue = InMemoryQueue()
        queue.put(Job(
                method="GET",
                path="/users",
                timeout=1,
                deadline_s=2,
                payload={"name": "John", "id": 10},
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": "Bearer demo-token",
                    "X-Request-ID": "req-123",
                },
                idempotency_key="x101x2555200",
            ))
        worker = Worker(queue, client)
        response = worker.run_once()

        assert attempts == 2
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        assert response.request.method == "GET"
        assert response.request.url.path == "/users"
        assert response.request.headers["Idempotency-Key"] == "x101x2555200"
        assert len(idempotency_keys) == 2
        for k in idempotency_keys:
            assert k == "x101x2555200"
        assert idempotency_keys[0] == idempotency_keys[1]
        assert status[0] == 503
        assert status[1] == 200
        assert status == [503, 200]
        assert idempotency_keys == ["x101x2555200", "x101x2555200"]