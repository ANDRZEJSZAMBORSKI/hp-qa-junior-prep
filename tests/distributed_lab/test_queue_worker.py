from distributed_lab.queue_worker import Job, InMemoryQueue, parse_job, Worker
from lab_fw.core.errors import SchemaError
import pytest
from lab_fw.api.client import ApiClient
import httpx
from lab_fw.core.errors import ApiError, HttpStatusError
import sys

@pytest.mark.distributed_lab
def test_job_get():
    data = {
        "method": "GET",
        "path": "/user"
    }
    job = parse_job(data)
    assert isinstance(job, Job)
    assert job.method == "GET"
    assert job.path == "/user"
    assert job.model_dump() == {
                                        "method": "GET",
                                        "path": "/user",
                                        'timeout': None,
                                        'deadline_s': None,
                                        'payload': None,
                                        'headers': {},
                                        'idempotency_key': None,
    
                                    }
    queue = InMemoryQueue()
    assert queue.get() is None
    queue.put(job)
    assert queue.get() is job

@pytest.mark.distributed_lab
def test_job_get_invalid():
    data = {
        "method": "TRACE",
        "path": "/user"
    }
    with pytest.raises(SchemaError, match="Job schema validation failed"):
        parse_job(data)

@pytest.mark.distributed_lab
def test_queue_fifo():
    queue = InMemoryQueue()
    queue.put(parse_job({"method": "GET", "path": "/users"}))
    queue.put(parse_job({"method": "POST", "path": "/users"}))
    assert queue.get().method == "GET"
    assert queue.get().method == "POST"
    assert queue.get() is None

@pytest.mark.distributed_lab
def test_two_queues():
    queue1 = InMemoryQueue()
    queue1.put(parse_job({"method": "GET", "path": "/users"}))
    queue2 = InMemoryQueue()
    assert queue2.get() is None
    assert queue1.get().method == "GET"

@pytest.mark.distributed_lab   
def test_worker():
    with ApiClient() as client:
        queue = InMemoryQueue()
        worker = Worker(queue, client)
        assert worker.run_once() is None

@pytest.mark.distributed_lab
def test_worker_api_handler():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(200, json={"items": [1, 2]})
        if request.method == "POST":
            return httpx.Response(201, json={"items": [3, 4]})
        return httpx.Response(405, json={"error": "Method not allowed"})
    transport = httpx.MockTransport(handler)
    with ApiClient(transport=transport) as client:
        queue = InMemoryQueue()
        queue.put(parse_job({"method": "GET", "path": "/users"}))
        queue.put(parse_job({"method": "POST", "path": "/users"}))
        queue.put(parse_job({"method": "DELETE", "path": "/users"}))
        worker = Worker(queue, client)
        response = worker.run_once()
        assert response.status_code == 200
        assert response.json() == {"items": [1, 2]}
        assert response.request.method == "GET"
        assert response.request.url.path == "/users"
        assert response.is_success
        assert response.text == '{"items":[1,2]}'
        response = worker.run_once()
        assert response.status_code == 201
        assert response.json() == {"items": [3, 4]}
        assert response.request.method == "POST"
        assert response.request.url.path == "/users"
        assert response.is_success
        assert response.text == '{"items":[3,4]}'
        with pytest.raises(NotImplementedError, match="is not supported by ApiClient"):
            worker.run_once()
        assert worker.run_once() is None

@pytest.mark.distributed_lab
def test_worker_api_handler_500():
    requests_count = 0
    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal requests_count
        requests_count += 1
        return httpx.Response(500, json={"error": "Internal Server Error"}, request=request)

    transport = httpx.MockTransport(handler)
    with ApiClient(transport=transport) as client:
        queue = InMemoryQueue()
        queue.put(parse_job({"method": "GET", "path": "/users"}))
        worker = Worker(queue, client)
        with pytest.raises(HttpStatusError, match="GET /users failed with HTTP 500:") as exc_info:
            worker.run_once()
        
    assert requests_count == 1
    assert isinstance(exc_info.value, HttpStatusError)

    assert str(exc_info.value) == 'GET /users failed with HTTP 500: {"error":"Internal Server Error"}'
    assert exc_info.value.args[0] == 'GET /users failed with HTTP 500: {"error":"Internal Server Error"}'
    assert exc_info.value.response.request.url.path == "/users"
    assert exc_info.value.response.request.method == "GET"
    assert exc_info.value.response.status_code == 500
    assert exc_info.value.response.json() == {"error": "Internal Server Error"}
    assert exc_info.value.response.text == '{"error":"Internal Server Error"}'

@pytest.mark.distributed_lab
@pytest.mark.parametrize(
    "status",
    [400, 401, 403, 404, 422, 500],
    ids=[
        "bad_request",
        "unauthorized",
        "forbidden",
        "not_found",
        "unprocessable_entity",
        "internal_server_error",
    ],
)
def test_get_does_not_retry_non_retryable_status(settings, status):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            return httpx.Response(status, request=request)

        return httpx.Response(
            200,
            request=request,
            json={"ok": True},
        )

    transport = httpx.MockTransport(handler)
    with ApiClient(settings, transport=transport) as client:
        queue = InMemoryQueue()
        queue.put(parse_job({"method": "GET", "path": "/users"}))
        worker = Worker(queue, client)
        with pytest.raises(HttpStatusError):
            worker.run_once()
        assert attempts == 1

@pytest.mark.distributed_lab
@pytest.mark.parametrize(
    "status",
    [429, 503],
    ids=[
        "too_many_requests",
        "service_unavailable",
        ],
)
def test_get_retry_retryable_status(settings, status):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            return httpx.Response(status, request=request)

        return httpx.Response(
            200,
            request=request,
            json={"ok": True},
        )

    transport = httpx.MockTransport(handler)
    
    with ApiClient(settings, transport=transport) as client:
        queue = InMemoryQueue()
        queue.put(parse_job({"method": "GET", "path": "/users"}))
        worker = Worker(queue, client)
        response = worker.run_once()

        assert attempts == 3
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        assert response.request.method == "GET"
        assert response.request.url.path == "/users"

@pytest.mark.distributed_lab
@pytest.mark.parametrize(
    "error_type",
    [
        httpx.ConnectError,
        httpx.ReadTimeout,
    ],
    ids=[
        "connect_error",
        "read_timeout",
    ],
)
def test_get_retries_transport_error_then_succeeds(settings, error_type):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            raise error_type("transport failed", request=request)
        return httpx.Response(200, request=request, json={"id": 1, "name": "John"})

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        queue = InMemoryQueue()
        queue.put(parse_job({"method": "GET", "path": "/users"}))
        worker = Worker(queue, client)
        response = worker.run_once()

    assert attempts == 3
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "John"}
    assert response.request.method == "GET"
    assert response.request.url.path == "/users"

@pytest.mark.distributed_lab
@pytest.mark.parametrize(
    "error_type",
    [
        httpx.ConnectError,
        httpx.ReadTimeout,
    ],
    ids=[
        "connect_error",
        "read_timeout",
    ],
)
def test_post_does_not_retry_transport_error(settings, error_type):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            raise error_type("transport failed", request=request)
        return httpx.Response(200, request=request, json={"id": 1, "name": "John"})

    
    transport = httpx.MockTransport(handler)
    with ApiClient(settings, transport=transport) as client:
        queue = InMemoryQueue()
        queue.put(parse_job({"method": "POST", "path": "/users"}))
        worker = Worker(queue, client)
        with pytest.raises(ApiError) as e:
            worker.run_once()
        assert attempts == 1
        assert isinstance(e.value.__cause__, error_type)

@pytest.mark.distributed_lab
@pytest.mark.parametrize(
    "status",
    [429, 503],
    ids=[
        "too_many_requests",
        "service_unavailable",
        ],
)
def test_post_does_not_retry_retryable_status(settings, status):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            return httpx.Response(status, request=request)

        return httpx.Response(
            200,
            request=request,
            json={"ok": True},
        )

    transport = httpx.MockTransport(handler)
    
    with ApiClient(settings, transport=transport) as client:
        queue = InMemoryQueue()
        queue.put(parse_job({"method": "POST", "path": "/users"}))
        worker = Worker(queue, client)
        with pytest.raises(HttpStatusError):
            worker.run_once()
        assert attempts == 1

@pytest.mark.distributed_lab
def test_get_retry_exhausted_429(settings):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(429, request=request)

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        queue = InMemoryQueue()
        queue.put(parse_job({"method": "GET", "path": "/users"}))
        worker = Worker(queue, client)

        with pytest.raises(HttpStatusError) as exc_info:
            worker.run_once()

    assert attempts == 3
    assert exc_info.value.response.status_code == 429
    assert exc_info.value.response.request.method == "GET"
    assert exc_info.value.response.request.url.path == "/users"

@pytest.mark.distributed_lab
def test_get_retry_exhausted_transport_error(settings):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ConnectError("transport failed", request=request)

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        queue = InMemoryQueue()
        queue.put(parse_job({"method": "GET", "path": "/users"}))
        worker = Worker(queue, client)

        with pytest.raises(ApiError) as exc_info:
            worker.run_once()

    assert attempts == 3
    assert isinstance(exc_info.value.__cause__, httpx.ConnectError)
    assert str(exc_info.value.__cause__) == "transport failed"
    assert str(exc_info.value) == "GET /users failed: transport failed"
    assert exc_info.value.__cause__.request.method == "GET"
    assert exc_info.value.__cause__.request.url.path == "/users"

@pytest.mark.distributed_lab
def test_queue_rejects_non_job():
    queue = InMemoryQueue()
    with pytest.raises(TypeError, match="expected type Job"):
        queue.put("Hahaha")

@pytest.mark.distributed_lab
def test_parse_job_missing_path():
    data = {
        "method": "GET",
    }

    with pytest.raises(SchemaError, match="Job schema validation failed:"):
        parse_job(data)

@pytest.mark.distributed_lab
def test_parse_job_extra_field():
    
    data = {
        "method": "GET",
        "path": "/users",
        "unknown": "value",
    }

    with pytest.raises(SchemaError, match="Job schema validation failed:"):
        parse_job(data)

@pytest.mark.distributed_lab
def test_parse_job_invalid_path_type():
    
    data = {
        "method": "GET",
        "path": 123,
    }

    with pytest.raises(SchemaError, match="Job schema validation failed:"):
        parse_job(data)

@pytest.mark.distributed_lab
def test_parse_job_invalid_timeout_type():
    
    data = {
        "method": "GET",
        "path": "/users",
        "timeout": "5",
    }

    with pytest.raises(SchemaError, match="Job schema validation failed:"):
        parse_job(data)

@pytest.mark.distributed_lab
def test_parse_job_invalid_deadline_type():
    
    data = {
        "method": "GET",
        "path": "/users",
        "deadline_s": "10",
    }

    with pytest.raises(SchemaError, match="Job schema validation failed:"):
        parse_job(data)

@pytest.mark.distributed_lab
def test_parse_job_missing_method():

    data = {
        "path": "/users",
    }

    with pytest.raises(SchemaError, match="Job schema validation failed:"):
        parse_job(data)

@pytest.mark.distributed_lab
def test_parse_job_invalid_method():
    
    data = {
        "method": "TRACE",
        "path": "/users",
    }

    with pytest.raises(SchemaError, match="Job schema validation failed:"):
        parse_job(data)

@pytest.mark.distributed_lab
def test_parse_job_accepts_none_timeout_and_deadline():
    
    data = {
        "method": "GET",
        "path": "/users",
        "timeout": None,
        "deadline_s": None,
    }

    job = parse_job(data)
    assert job.timeout is None
    assert job.deadline_s is None

@pytest.mark.distributed_lab
def test_parse_job_accepts_numeric_timeout_and_deadline():
   
    data = {
        "method": "GET",
        "path": "/users",
        "timeout": 5.0,
        "deadline_s": 10.0,
    }

    job = parse_job(data)
    assert isinstance(job.timeout, float)
    assert job.timeout == 5.0
    assert isinstance(job.deadline_s, float)
    assert job.deadline_s == 10.0

@pytest.mark.distributed_lab
def test_queue_get_empty_returns_none():
    
    queue = InMemoryQueue()

    assert queue.get() is None

@pytest.mark.distributed_lab
def test_queue_put_get_returns_same_job():
  
    queue = InMemoryQueue()
    job = Job(method="GET", path="/users")

    queue.put(job)
    assert queue.get() is job

@pytest.mark.distributed_lab
def test_queue_get_removes_job():
    
    queue = InMemoryQueue()
    job = Job(method="GET", path="/users")
    queue.put(job)

    assert queue.get() is job
    assert queue.get() is None

@pytest.mark.distributed_lab
def test_queue_fifo_order():
  
    queue = InMemoryQueue()
    first = Job(method="GET", path="/first")
    second = Job(method="POST", path="/second")
    third = Job(method="GET", path="/third")

    queue.put(first)
    queue.put(second)
    queue.put(third)
    assert queue.get() is first
    assert queue.get() is second
    assert queue.get() is third
    assert queue.get() is None

@pytest.mark.distributed_lab
def test_queue_rejects_none():
    
    queue = InMemoryQueue()

    with pytest.raises(TypeError,  match="expected type Job"):
        queue.put(None)

@pytest.mark.distributed_lab
def test_queue_rejects_list():
    
    queue = InMemoryQueue()

    with pytest.raises(TypeError,  match="expected type Job"):
        queue.put([])

@pytest.mark.distributed_lab
def test_queue_accepts_job_subclass():
    
    class SpecialJob(Job):
        pass

    queue = InMemoryQueue()
    job = SpecialJob(method="GET", path="/users")

    queue.put(job)
    assert queue.get() is job

@pytest.mark.distributed_lab
def test_queue_uses_provided_deque():
   
    from collections import deque

    first = Job(method="GET", path="/first")
    storage = deque([first])
    queue = InMemoryQueue(storage)

    assert len(storage) == 1
    assert queue._queue is storage
    assert queue.get() is first
    assert len(storage) == 0
    assert queue.get() is None

@pytest.mark.distributed_lab
def test_queue_creates_independent_storage_when_none_provided():
    
    first_queue = InMemoryQueue()
    second_queue = InMemoryQueue()
    job = Job(method="GET", path="/users")

    first_queue.put(job)
    assert len(first_queue._queue) == 1
    assert len(second_queue._queue) == 0
    assert first_queue._queue is not second_queue._queue  
    assert second_queue.get() is None
    assert first_queue.get() is job
    assert first_queue.get() is None

@pytest.mark.distributed_lab
def test_parse_job_default_optional_fields():
 
    data = {
        "method": "GET",
        "path": "/users",
    }

    job = parse_job(data)
    assert job.timeout is None
    assert job.deadline_s is None

@pytest.mark.distributed_lab
@pytest.mark.parametrize(
    "method",
    ["GET", "POST", "PUT", "PATCH", "DELETE"],
)
def test_parse_job_accepts_all_supported_methods(method):
    
    data = {
        "method": method,
        "path": "/users",
    }

    job = parse_job(data)
    assert job.method == method

@pytest.mark.distributed_lab
def test_parse_job_rejects_boolean_timeout():
    
    data = {
        "method": "GET",
        "path": "/users",
        "timeout": True,
    }

    with pytest.raises(SchemaError, match="Job schema validation failed:"):
        parse_job(data)

@pytest.mark.distributed_lab
def test_parse_job_rejects_boolean_deadline():
    
    data = {
        "method": "GET",
        "path": "/users",
        "deadline_s": True,
    }

    with pytest.raises(SchemaError, match="Job schema validation failed:"):
        parse_job(data)

@pytest.mark.distributed_lab
def test_parse_job_rejects_boolean_path():
    
    data = {
        "method": "GET",
        "path": True,
    }

    with pytest.raises(SchemaError, match="Job schema validation failed:"):
        parse_job(data)

@pytest.mark.distributed_lab
def test_parse_job_rejects_empty_data():
    
    data = {}

    with pytest.raises(SchemaError, match="Job schema validation failed:"):
        parse_job(data)

@pytest.mark.distributed_lab
def test_worker_empty_queue_does_not_call_api(monkeypatch):

    queue = InMemoryQueue()

    calls = 0

    class FakeApiClient:
        def get(self, path, **kwargs):
            nonlocal calls
            calls += 1
            return

    monkeypatch.setattr(
                            sys.modules[__name__],
                            "ApiClient",
                            FakeApiClient,
                        )

    worker = Worker(queue, ApiClient())
    assert worker.run_once() is None
    assert calls == 0

@pytest.mark.distributed_lab
def test_worker_get_success(monkeypatch):

    queue = InMemoryQueue()
    queue.put(
        parse_job({
            "method": "GET",
            "path": "/test",
        })
    )
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

    worker = Worker(queue, ApiClient())

    
    response = worker.run_once()

    assert response is expected_response
    assert calls == [("/test", {"headers": {}})]

@pytest.mark.distributed_lab
def test_worker_post_success(monkeypatch):
    queue = InMemoryQueue()
    queue.put(
        parse_job({
            "method": "POST",
            "path": "/test",
        })
    )

    expected_response = httpx.Response(200)
    calls = []

    class FakeApiClient:
        def post(self, path, **kwargs):
            calls.append((path, kwargs))
            return expected_response

    monkeypatch.setattr(
                            sys.modules[__name__],
                            "ApiClient",
                            FakeApiClient,
                        )

    worker = Worker(queue, ApiClient())   

    response = worker.run_once()

    assert response is expected_response
    assert calls == [("/test", {"headers": {}})]

@pytest.mark.distributed_lab
def test_worker_uses_job_timeout(monkeypatch):
    
    queue = InMemoryQueue()
    queue.put(Job(method="GET", path="/test", timeout=2.5))
    
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

    worker = Worker(queue, ApiClient())   

    response = worker.run_once()

    assert response is expected_response
    assert calls == [
                        ("/test", {"timeout": 2.5, "headers": {}})
                    ]


@pytest.mark.distributed_lab
def test_job_http_fields_default_values() -> None:
    # Verify that optional HTTP data has the expected defaults.
    job = Job(method="POST", path="/items")

    assert job.payload is None
    assert job.headers == {}
    assert job.idempotency_key is None


@pytest.mark.distributed_lab
def test_job_accepts_json_headers_and_idempotency_key() -> None:
    # Verify that Job preserves the supplied HTTP request data.
    payload = {"name": "x"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token",
    }
    key = "item-create-001"

    job = Job(
        method="POST",
        path="/items",
        payload=payload,
        headers=headers,
        idempotency_key=key,
    )

    assert job.payload == payload
    assert job.headers == headers
    assert job.idempotency_key == key


@pytest.mark.distributed_lab
def test_worker_passes_headers_and_idempotency_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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

    original_headers = job.headers.copy()
    original_payload = job.payload.copy()

    calls = []

    class FakeApiClient:
        def post(self, path, **kwargs):
            calls.append((path, kwargs))

            request = httpx.Request(
                "POST",
                f"http://testserver{path}",
                json=kwargs.get("json"),
                headers=kwargs.get("headers"),
            )

            expected_response = httpx.Response(
                200,
                json={"items": [3, 4]},
                request=request,
            )
            return expected_response

    monkeypatch.setattr(
        sys.modules[__name__],
        "ApiClient",
        FakeApiClient,
    )

    worker = Worker(queue, ApiClient())
    assert "idempotency-key" not in worker._queue._queue[0].headers
    assert "Idempotency-Key" not in job.headers
    response = worker.run_once()

    # Verify the returned response.
    assert response is not None
    assert isinstance(response, httpx.Response)
    assert response.status_code == 200
    assert response.is_success
    assert response.json() == {"items": [3, 4]}
    assert response.content == b'{"items":[3,4]}'
    assert response.text == '{"items":[3,4]}'
    assert response.content == b'{"items":[3,4]}'
    assert len(response.content) == len(response.text.encode("utf-8"))
    # Verify the request method and complete URL.
    assert response.request.method == "POST"
    assert str(response.request.url) == "http://testserver/test"
    assert response.request.url == httpx.URL("http://testserver/test")

    # Verify individual URL components.
    assert response.request.url.scheme == "http"
    assert response.request.url.host == "testserver"
    assert response.request.url.port is None
    assert response.request.url.path == "/test"
    assert response.request.url.query == b""
    assert response.request.url.fragment == ""
    assert response.request.url.raw_path == b"/test"
    assert response.request.url.is_absolute_url
    assert response.request.url.scheme == "http"

    # Verify the request body.
    assert response.request.content
    assert response.request.content == b'{"name":"John","id":10}'
    assert response.request.read() == b'{"name":"John","id":10}'
    assert response.request.content == b'{"name":"John","id":10}'
    assert response.request.read() == b'{"name":"John","id":10}'

    # Verify automatically generated request headers.
    assert response.request.headers["host"] == "testserver"
    assert response.request.headers["content-type"] == "application/json"
    assert response.request.headers["content-length"] == str(
                                                                len(response.request.content)
                                                            )

    # Verify user-supplied request headers.
    assert response.request.headers["accept"] == "application/json"
    assert response.request.headers["authorization"] == "Bearer demo-token"
    assert response.request.headers["x-request-id"] == "req-123"

    # Verify the idempotency header.
    assert response.request.headers["idempotency-key"] == "x101x2555200"

    # Verify response headers separately from request headers.
    assert response.headers["content-type"] == "application/json"
    assert int(response.headers["content-length"]) == len(response.content)

    # Verify the number of API calls.
    assert len(calls) == 1

    # Inspect the arguments passed to post().
    path, kwargs = calls[0]

    assert path == "/test"
    assert kwargs["timeout"] == 2.5
    assert kwargs["json"] == {"name": "John", "id": 10}

    # Verify the exact headers passed by Worker.
    assert kwargs["headers"]["Content-Type"] == "application/json"
    assert kwargs["headers"]["Accept"] == "application/json"
    assert kwargs["headers"]["Authorization"] == "Bearer demo-token"
    assert kwargs["headers"]["X-Request-ID"] == "req-123"
    assert kwargs["headers"]["Idempotency-Key"] == "x101x2555200"

    # Verify the complete call and all its arguments.
    assert calls == [
        (
            "/test",
            {
                "timeout": 2.5,
                "json": {"name": "John", "id": 10},
                "headers": {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": "Bearer demo-token",
                    "X-Request-ID": "req-123",
                    "Idempotency-Key": "x101x2555200",
                },
            },
        )
    ]

    # Verify Worker did not mutate the original Job data.
    assert job.headers == original_headers
    assert "Idempotency-Key" not in job.headers
    assert "idempotency-key" not in job.headers
    assert job.payload == original_payload
    assert job.idempotency_key == "x101x2555200"

    # Verify the job was consumed from the queue.
    assert queue.get() is None

    # Verify the queue remains empty.
    assert queue.get() is None

