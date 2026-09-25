import httpx
import pytest
import json
from lab_fw.api.client import ApiClient
from lab_fw.core.errors import ApiError
from lab_fw.core.retry import retry_call
from functools import wraps
import logging
from unittest.mock import patch

@pytest.mark.mocks
@pytest.mark.mocks_httpx
def test_mock_transport_get_and_post(settings):
    captured_request = None
    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        if request.method == "GET":
            return httpx.Response(200, json={"items": [1, 2]})
        if request.method == "POST":
            return httpx.Response(201, json={"items": [3, 4]})

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        response = client.get(
                                "/users",
                                params={"page": "2"},
                                headers={"X-Test": "hello"},
                            )

    assert response.status_code == 200
    assert response.json() == {"items": [1, 2]}
    assert captured_request.method == "GET"
    assert captured_request.url.path == "/users"
    assert captured_request.url.params["page"] == "2"
    assert captured_request.headers["X-Test"] == "hello"

    with ApiClient(settings, transport=transport) as client:
        response = client.post(
                                "/users",
                                params={"page": "2"},
                                headers={"X-Test": "hello"},
                            )

    assert response.status_code == 201
    assert response.json() == {"items": [3, 4]}
    assert captured_request.method == "POST"
    assert captured_request.url.path == "/users"
    assert captured_request.url.params["page"] == "2"
    assert captured_request.headers["X-Test"] == "hello"

@pytest.mark.mocks
@pytest.mark.mocks_httpx
@pytest.mark.parametrize(
    "method,status,body",
    [
        ("GET", 200, {"items": [1, 2]}),
        ("POST", 201, {"items": [3, 4]}),
    ],
    ids=["get", "post"],
)
def test_mock_transport_method(method, status, body, settings):
    captured_request = None
    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(status, json=body)

    with ApiClient(settings, transport=httpx.MockTransport(handler)) as client:
        call = client.get if method == "GET" else client.post
        response = call(
            "/users",
            params={"page": "2"},
            headers={"X-Test": "hello"},
        )
    assert response.status_code == status
    assert response.json() == body
    assert captured_request.method == method
    assert captured_request.url.path == "/users"
    assert captured_request.url.params["page"] == "2"
    assert captured_request.headers["X-Test"] == "hello"

@pytest.mark.mocks
@pytest.mark.mocks_httpx
def test_mock_transport_path(settings):
    def handler(request: httpx.Request) -> httpx.Response:
        resp = {
                "/users/1": (200, {"id": 1,"name": "John",}),
                "/users/2": (404, {"error": "User not found",}),
                "/users/3": (500, {"error": "Internal Server Error",}),
                "/users/text": (200, "not json"),
        }
        key = request.url.path
        if key == "/users/text":
            return httpx.Response(200, text="not json")
        status, body = resp.get(key, (404, {"error": "User not found"}))
        return httpx.Response(status, json=body)

    with ApiClient(settings, transport=httpx.MockTransport(handler)) as client:
        response = client.get("/users/1")
        assert response.status_code == 200
        assert response.json() == {"id": 1,"name": "John"}
        response = client.get("/users/2")
        assert response.status_code == 404 
        assert response.json() == {"error": "User not found"}
        response = client.get("/users/3")
        assert response.status_code == 500
        assert response.json() == {"error": "Internal Server Error"}
        with pytest.raises(json.JSONDecodeError):
            response = client.get("/users/text")
            response.json()

@pytest.mark.mocks
@pytest.mark.mocks_httpx
@pytest.mark.parametrize(
    "path,code,jsn",
    [
        ("/users/1", 200, {"id": 1,"name": "John"}),
        ("/users/2", 404, {"error": "User not found"}),
        ("/users/3", 500, {"error": "Internal Server Error"}),
        ("/users/text", 200, "not json"),
    ],
    ids=["json_1", "json_2", "json_3", "no_json"],
)
def test_mock_transport_path_2(path, code, jsn, settings):
    def handler(request: httpx.Request) -> httpx.Response:
        resp = {
                "/users/1": (200, {"id": 1,"name": "John",}),
                "/users/2": (404, {"error": "User not found",}),
                "/users/3": (500, {"error": "Internal Server Error",}),
        }
        key = request.url.path
        if key == "/users/text":
            return httpx.Response(200, text="not json")
        status, body = resp.get(key, (404, {"error": "User not found"}))
        return httpx.Response(status, json=body)

    with ApiClient(settings, transport=httpx.MockTransport(handler)) as client:
        response = client.get(path)
        assert response.status_code == code
        if path == "/users/text":
            with pytest.raises(json.JSONDecodeError):
                response.json()
        else:
            assert response.json() == jsn

@pytest.mark.mocks
@pytest.mark.mocks_httpx
def test_mock_transport_connect_error(settings):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError(
            "connection failed",
            request=request,
        )       
    
    transport = httpx.MockTransport(handler)
    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(ApiError, match="GET /users") as ei:
            client.get("/users")
        assert isinstance(ei.value.__cause__, httpx.ConnectError)

@pytest.mark.mocks
@pytest.mark.mocks_httpx
def test_mock_transport_read_timeout(settings):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout(
            "read timeout",
            request=request,
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(ApiError, match="GET /users") as ei:
            client.get("/users")
        assert isinstance(ei.value.__cause__, httpx.ReadTimeout)

@pytest.mark.mocks
@pytest.mark.mocks_httpx
@pytest.mark.parametrize(
    "error,msg",
    [
        (httpx.ConnectError, "connection failed"),
        (httpx.ReadTimeout, "read timeout"),
    ],
    ids=["connection failed", "read timeout"],
)
def test_mock_transport_read_timeout_connect_error(error, msg, settings):
    def handler(request: httpx.Request) -> httpx.Response:
        raise error(
            msg,
            request=request,
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(ApiError, match="GET /users") as ei:
            client.get("/users")
        assert isinstance(ei.value.__cause__, error)

@pytest.mark.mocks
@pytest.mark.mocks_httpx
def test_mock_transport_logs_request(caplog, settings):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError(
            "connection failed",
            request=request,
        )
    
    transport = httpx.MockTransport(handler)
    with ApiClient(settings, transport=transport) as client:
        with caplog.at_level("INFO", logger="lab_fw.api"):
            with pytest.raises(ApiError):
                client.get("/users")
    assert "GET /users" in caplog.text
    for record in caplog.records:
        print(record.name)
        print(record.levelname)
        print(record.message)

@pytest.mark.mocks
@pytest.mark.mocks_httpx
def test_mock_transport_with_retry(settings):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            raise httpx.ConnectError(
                "temporary failure",
                request=request,
            )

        return httpx.Response(
            200,
            json={"status": "ok"},
        )

    transport = httpx.MockTransport(handler)
    with ApiClient(settings, transport=transport) as client:
        response = retry_call(lambda: client.get("/users"), delay_s = 0, retry_on = (ApiError,))
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        assert attempts == 3

retry_logger = logging.getLogger("lab_fw.core.retry")

def retry(times: int = 3, exc_types=(Exception,)):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            last = None
            for i in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except exc_types as e:
                    retry_logger.warning("attempt %s/%s failed: %s", i, times, e)
                    last = e
            raise last
        return wrapper
    return  decorator

@pytest.mark.mocks
@pytest.mark.mocks_httpx
def test_mock_transport_with_my_retry(settings):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            raise httpx.ConnectError(
                "temporary failure",
                request=request,
            )

        return httpx.Response(
            200,
            json={"status": "ok"},
        )

    transport = httpx.MockTransport(handler)

    @retry(exc_types= (ApiError,))
    def call_retry(fn):
        return fn()

    with ApiClient(settings, transport=transport) as client:
        response = call_retry(lambda: client.get("/users"))
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        assert attempts == 3

@pytest.mark.mocks
@pytest.mark.mocks_httpx
def test_mock_transport_with_retry_exhausted(settings):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ConnectError(
            "temporary failure",
            request=request,
        )
    
    transport = httpx.MockTransport(handler)
    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(ApiError, match="GET /users") as ei:
            retry_call(lambda: client.get("/users"), delay_s = 0, retry_on = (ApiError,))
        assert isinstance(ei.value.__cause__, httpx.ConnectError)
        assert attempts == 3 

@pytest.mark.mocks
@pytest.mark.mocks_httpx
def test_mock_transport_reporting_step(settings):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"items": [1, 2]})

    transport = httpx.MockTransport(handler)

    with patch("lab_fw.api.client.step") as mock_step:
        with ApiClient(settings, transport=transport) as client:
            response = client.get("/users")

    assert response.status_code == 200
    mock_step.assert_called_once_with("GET /users")


@pytest.mark.mocks
@pytest.mark.mocks_httpx
def test_mock_transport_reporting_attach_json(settings):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"items": [1, 2]})

    transport = httpx.MockTransport(handler)

    with patch("lab_fw.api.client.attach_json") as mock_attach_json:
        with ApiClient(settings, transport=transport) as client:
            response = client.get("/users")

    assert response.status_code == 200
    assert response.json() == {"items": [1, 2]}
    mock_attach_json.assert_called_once_with("response", {"status": 200, "body": '{"items":[1,2]}',})

@pytest.mark.mocks
@pytest.mark.mocks_httpx
def test_mock_transport_reporting_attach_json_truncates_body(settings):
    body = "x" * 1500

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=body)

    transport = httpx.MockTransport(handler)

    with patch("lab_fw.api.client.attach_json") as mock_attach_json:
        with ApiClient(settings, transport=transport) as client:
            response = client.get("/users")

    assert response.status_code == 200
    assert len(response.text) == 1500

    mock_attach_json.assert_called_once()

    args, kwargs = mock_attach_json.call_args

    assert args[0] == "response"
    assert args[1]["status"] == 200
    assert args[1]["body"] == "x" * 1000
    assert len(args[1]["body"]) == 1000