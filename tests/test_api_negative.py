import httpx
import pytest
import re
from lab_fw.api.client import ApiClient, ensure_success
from lab_fw.core.errors import ApiError, HttpStatusError, SchemaError
from lab_fw.api.schemas import parse_user
from lab_fw.core.retry import retry_call
from functools import wraps
import logging

@pytest.mark.api
@pytest.mark.parametrize(
    "status",
    [400, 401, 403, 404, 422, 500, 503],
    ids=[
        "bad_request",
        "unauthorized",
        "forbidden",
        "not_found",
        "unprocessable_entity",
        "internal_server_error",
        "service_unavailable",
    ],
)
def test_http_status_error(status, settings):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status,
            json={"error": f"HTTP {status}"},
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        response = client.get("/users/999")

    with pytest.raises(
        HttpStatusError,
        match=rf"GET /users/999 failed with HTTP {status}",
    ):
        ensure_success(response)

    with pytest.raises(
        HttpStatusError,
        match=rf'GET /users/999 failed with HTTP {status}: {re.escape(response.text)}',
    ):
        ensure_success(response)

    with pytest.raises(
            HttpStatusError,
            match=r'GET /users/999',
        ):
            ensure_success(response)

    assert response.request.url.path == "/users/999"
    assert response.request.method == "GET"
    assert response.status_code == status
    assert response.json() == {"error": f"HTTP {status}"}
    assert response.text == f'{{"error":"HTTP {status}"}}'

@pytest.mark.api
def test_ensure_success_returns_response_for_success(settings):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                    "id": 1,
                    "name": "John",
                                },
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        response = client.get("/users/999")
        result = ensure_success(response)
        assert result is response

    assert response.request.url.path == "/users/999"
    assert response.request.method == "GET"
    assert response.status_code == 200
    assert response.json() == {
                                "id": 1,
                                "name": "John",
                                            }
    assert response.text == '{"id":1,"name":"John"}'

@pytest.mark.api
@pytest.mark.parametrize(
    "error_type",
    [httpx.ReadTimeout, httpx.ConnectError],
    ids=[
        "read_timeout",
        "connect_error",
    ],
)
def test_transport_error_becomes_api_error(error_type, settings):
    def handler(request: httpx.Request) -> httpx.Response:
        raise error_type(
            "transport failed",
            request=request,
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(ApiError) as exc_info:
            client.get("/users")

    assert isinstance(exc_info.value, ApiError)

    assert isinstance(
        exc_info.value.__cause__,
        error_type,
    )

    assert str(exc_info.value) == "GET /users failed: transport failed"
    assert exc_info.value.args[0] == "GET /users failed: transport failed"
    assert exc_info.value.__cause__.request.url.path == "/users"
    assert exc_info.value.__cause__.request.method == "GET"
    assert str(exc_info.value.__cause__) == "transport failed"
    assert exc_info.value.__cause__.args == ("transport failed",)
    assert exc_info.value.__cause__.args[0] == "transport failed"
    assert str(exc_info.value.__cause__) == exc_info.value.__cause__.args[0]
    assert isinstance(
                            exc_info.value.__cause__,
                            httpx.HTTPError,
                        )
    assert issubclass(
                            error_type,
                            httpx.HTTPError,
                        )

    assert isinstance(
                            exc_info.value.__cause__,
                            error_type,
                        )

    assert isinstance(exc_info.value, ApiError)
    assert exc_info.type is ApiError

@pytest.mark.api
def test_success_status_with_invalid_user_schema(settings):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "1",
                "name": "John",
            },
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        response = client.get("/users/1")

    response = ensure_success(response)

    assert response.request.url.path == "/users/1"
    assert response.request.method == "GET"
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "name": "John",
    }
    assert response.text == '{"id":"1","name":"John"}'

    with pytest.raises(
        SchemaError,
        match=r"User schema validation failed",
    ):
        parse_user(response.json())

@pytest.mark.api
def test_post_without_auth_returns_401(settings):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "error": "Unauthorized",
            },
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        response = client.post("/users/1")
        with pytest.raises(HttpStatusError, match=rf'POST /users/1 failed with HTTP 401: {re.escape(response.text)}') as exc_info:
            ensure_success(response)

        assert response.request.url.path == "/users/1"
        assert response.request.method == "POST"
        assert response.status_code == 401
        assert response.json() == {"error": "Unauthorized"}
        assert response.text == '{"error":"Unauthorized"}'

        assert isinstance(exc_info.value, HttpStatusError)
        assert isinstance(exc_info.value, ApiError)

        assert isinstance(
            exc_info.value,
            HttpStatusError,
        )

        assert str(exc_info.value) == f'POST /users/1 failed with HTTP 401: {response.text}'
        assert exc_info.value.args[0] == f'POST /users/1 failed with HTTP 401: {response.text}'
        assert str(exc_info.value) == f'POST /users/1 failed with HTTP 401: {response.text}'
        assert exc_info.value.args == (f'POST /users/1 failed with HTTP 401: {response.text}',)
        assert exc_info.value.args[0] == f'POST /users/1 failed with HTTP 401: {response.text}'
        assert str(exc_info.value) == exc_info.value.args[0]
        assert isinstance(
                                exc_info.value,
                                ApiError,
                            )
        assert issubclass(
                                HttpStatusError,
                                ApiError,
                            )

        assert isinstance(
                                exc_info.value,
                                HttpStatusError,
                            )

        assert isinstance(exc_info.value, ApiError)
        assert isinstance(exc_info.value, HttpStatusError)
        assert exc_info.type is HttpStatusError

@pytest.mark.api
def test_http_status_error_attaches_details(settings, monkeypatch):
    attached = []

    def fake_attach_json(name, data):
        attached.append((name, data))

    monkeypatch.setattr(
                            "lab_fw.api.client.attach_json",
                            fake_attach_json,
                        )
    
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            503,
            json={
                "error": "Service unavailable",
            },
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        response = client.get("/users")

    with pytest.raises(
        HttpStatusError,
        match=rf"GET /users failed with HTTP 503: "
              rf"{re.escape(response.text)}",
    ) as exc_info:
        ensure_success(response)

    assert len(attached) == 2
    assert attached[0][0] == "response"
    assert attached[0][1] == {
                                    "status": 503,
                                    "body": response.text,
                                }
    assert attached[0][1] == {
                                    "status": 503,
                                    "body": '{"error":"Service unavailable"}',
                                }
    assert attached[1][0] == "status_error"
    assert attached[1][1] == {
                                    "status": 503,
                                    "body": response.text,
                                }
    assert attached[1][1] == {
                                    "status": 503,
                                    "body": '{"error":"Service unavailable"}',
                                }
    
    
    assert response.request.url.path == "/users"
    assert response.request.method == "GET"
    assert response.status_code == 503
    assert response.json() == {"error": "Service unavailable",}
    assert response.text == '{"error":"Service unavailable"}'
    
    assert isinstance(exc_info.value, HttpStatusError)
    assert isinstance(exc_info.value, ApiError)
    
    assert isinstance(
                exc_info.value,
                HttpStatusError,
            )
    
    assert str(exc_info.value) == f'GET /users failed with HTTP 503: {response.text}'
    assert exc_info.value.args[0] == f'GET /users failed with HTTP 503: {response.text}'
    assert str(exc_info.value) == f'GET /users failed with HTTP 503: {response.text}'
    assert exc_info.value.args == (f'GET /users failed with HTTP 503: {response.text}',)
    assert exc_info.value.args[0] == f'GET /users failed with HTTP 503: {response.text}'
    assert str(exc_info.value) == exc_info.value.args[0]
    assert isinstance(
                                    exc_info.value,
                                    ApiError,
                                )
    assert issubclass(
                                    HttpStatusError,
                                    ApiError,
                                )
    
    assert isinstance(
                                    exc_info.value,
                                    HttpStatusError,
                                )
    
    assert isinstance(exc_info.value, ApiError)
    assert isinstance(exc_info.value, HttpStatusError)
    assert exc_info.type is HttpStatusError

@pytest.mark.api
def test_retry_does_not_retry_404(settings):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        return httpx.Response(
            404,
            json={"error": "Not found"},
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(
            HttpStatusError,
            match=r"GET /users/999 failed with HTTP 404",
        ) as exc_info:
            retry_call(
                lambda: ensure_success(client.get("/users/999")),
                delay_s=0,
                retry_on=(ApiError,),
                retry_if = True,
            )

    assert attempts == 1

    assert isinstance(exc_info.value, HttpStatusError)
    assert isinstance(exc_info.value, ApiError)
    
    assert isinstance(
                exc_info.value,
                HttpStatusError,
            )
    
    assert str(exc_info.value) == 'GET /users/999 failed with HTTP 404: {"error":"Not found"}'
    assert exc_info.value.args[0] == 'GET /users/999 failed with HTTP 404: {"error":"Not found"}'
    assert str(exc_info.value) == 'GET /users/999 failed with HTTP 404: {"error":"Not found"}'
    assert exc_info.value.args == ('GET /users/999 failed with HTTP 404: {"error":"Not found"}',)
    assert exc_info.value.args[0] == 'GET /users/999 failed with HTTP 404: {"error":"Not found"}'
    assert str(exc_info.value) == exc_info.value.args[0]
    assert isinstance(
                                    exc_info.value,
                                    ApiError,
                                )
    assert issubclass(
                                    HttpStatusError,
                                    ApiError,
                                )
    
    assert isinstance(
                                    exc_info.value,
                                    HttpStatusError,
                                )
    
    assert isinstance(exc_info.value, ApiError)
    assert isinstance(exc_info.value, HttpStatusError)
    assert exc_info.type is HttpStatusError


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
                    if isinstance(e, HttpStatusError) and e.response and e.response.status_code not in (429, 503):
                        raise last
            raise last
        return wrapper
    return  decorator

@pytest.mark.api
def test_retry_does_not_retry_404_my_retry(settings):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        return httpx.Response(
            404,
            json={"error": "Not found"},
        )

    @retry(exc_types=(ApiError,))
    def call_retry(fn):
        return fn()

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(
            HttpStatusError,
            match=r"GET /users/999 failed with HTTP 404",
        ) as exc_info:
            call_retry(
                lambda: ensure_success(client.get("/users/999"))
            )

    assert attempts == 1

    assert isinstance(exc_info.value, HttpStatusError)
    assert isinstance(exc_info.value, ApiError)
    
    assert isinstance(
                exc_info.value,
                HttpStatusError,
            )
    
    assert str(exc_info.value) == 'GET /users/999 failed with HTTP 404: {"error":"Not found"}'
    assert exc_info.value.args[0] == 'GET /users/999 failed with HTTP 404: {"error":"Not found"}'
    assert str(exc_info.value) == 'GET /users/999 failed with HTTP 404: {"error":"Not found"}'
    assert exc_info.value.args == ('GET /users/999 failed with HTTP 404: {"error":"Not found"}',)
    assert exc_info.value.args[0] == 'GET /users/999 failed with HTTP 404: {"error":"Not found"}'
    assert str(exc_info.value) == exc_info.value.args[0]
    assert isinstance(
                                    exc_info.value,
                                    ApiError,
                                )
    assert issubclass(
                                    HttpStatusError,
                                    ApiError,
                                )
    
    assert isinstance(
                                    exc_info.value,
                                    HttpStatusError,
                                )
    
    assert isinstance(exc_info.value, ApiError)
    assert isinstance(exc_info.value, HttpStatusError)
    assert exc_info.type is HttpStatusError


@pytest.mark.api
def test_retry_does_not_retry_500_my_retry(settings):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        return httpx.Response(
            500,
            json={"error": "Not found"},
        )

    @retry(exc_types=(ApiError,))
    def call_retry(fn):
        return fn()

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(
            HttpStatusError,
            match=r"GET /users/999 failed with HTTP 500",
        ) as exc_info:
            call_retry(
                lambda: ensure_success(client.get("/users/999"))
            )

    assert attempts == 1

    assert isinstance(exc_info.value, HttpStatusError)
    assert isinstance(exc_info.value, ApiError)
    
    assert isinstance(
                exc_info.value,
                HttpStatusError,
            )
    
    assert str(exc_info.value) == 'GET /users/999 failed with HTTP 500: {"error":"Not found"}'
    assert exc_info.value.args[0] == 'GET /users/999 failed with HTTP 500: {"error":"Not found"}'
    assert str(exc_info.value) == 'GET /users/999 failed with HTTP 500: {"error":"Not found"}'
    assert exc_info.value.args == ('GET /users/999 failed with HTTP 500: {"error":"Not found"}',)
    assert exc_info.value.args[0] == 'GET /users/999 failed with HTTP 500: {"error":"Not found"}'
    assert str(exc_info.value) == exc_info.value.args[0]
    assert isinstance(
                                    exc_info.value,
                                    ApiError,
                                )
    assert issubclass(
                                    HttpStatusError,
                                    ApiError,
                                )
    
    assert isinstance(
                                    exc_info.value,
                                    HttpStatusError,
                                )
    
    assert isinstance(exc_info.value, ApiError)
    assert isinstance(exc_info.value, HttpStatusError)
    assert exc_info.type is HttpStatusError

@pytest.mark.api
@pytest.mark.parametrize(
    "status",
    [429, 503],
    ids=[
        "too_many_requests",
        "service_unavailable",
    ],
)
def test_retry_retries_5xx_my_retry(settings, status):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        return httpx.Response(
            status,
            json={"error": "Not found"},
        )

    @retry(exc_types=(ApiError,))
    def call_retry(fn):
        return fn()

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(
            HttpStatusError,
            match=rf"GET /users/999 failed with HTTP {status}",
        ) as exc_info:
            call_retry(
                lambda: ensure_success(client.get("/users/999"))
            )

    assert attempts == 3

    assert isinstance(exc_info.value, HttpStatusError)
    assert isinstance(exc_info.value, ApiError)
    
    assert isinstance(
                exc_info.value,
                HttpStatusError,
            )
    
    assert str(exc_info.value) == f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert exc_info.value.args[0] == f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert str(exc_info.value) == f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert exc_info.value.args == (f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}',)
    assert exc_info.value.args[0] == f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert str(exc_info.value) == exc_info.value.args[0]
    assert isinstance(
                                    exc_info.value,
                                    ApiError,
                                )
    assert issubclass(
                                    HttpStatusError,
                                    ApiError,
                                )
    
    assert isinstance(
                                    exc_info.value,
                                    HttpStatusError,
                                )
    
    assert isinstance(exc_info.value, ApiError)
    assert isinstance(exc_info.value, HttpStatusError)
    assert exc_info.type is HttpStatusError



@pytest.mark.api
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
def test_retry_no_retry_my_retry(settings, status):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        return httpx.Response(
            status,
            json={"error": "Not found"},
        )

    @retry(exc_types=(ApiError,))
    def call_retry(fn):
        return fn()

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(
            HttpStatusError,
            match=rf"GET /users/999 failed with HTTP {status}",
        ) as exc_info:
            call_retry(
                lambda: ensure_success(client.get("/users/999"))
            )

    assert attempts == 1

    assert isinstance(exc_info.value, HttpStatusError)
    assert isinstance(exc_info.value, ApiError)
    
    assert isinstance(
                exc_info.value,
                HttpStatusError,
            )
    
    assert str(exc_info.value) == f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert exc_info.value.args[0] == f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert str(exc_info.value) == f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert exc_info.value.args == (f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}',)
    assert exc_info.value.args[0] == f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert str(exc_info.value) == exc_info.value.args[0]
    assert isinstance(
                                    exc_info.value,
                                    ApiError,
                                )
    assert issubclass(
                                    HttpStatusError,
                                    ApiError,
                                )
    
    assert isinstance(
                                    exc_info.value,
                                    HttpStatusError,
                                )
    
    assert isinstance(exc_info.value, ApiError)
    assert isinstance(exc_info.value, HttpStatusError)
    assert exc_info.type is HttpStatusError



@pytest.mark.api
def test_retry_does_not_retry_404_retry(settings):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        return httpx.Response(
            404,
            json={"error": "Not found"},
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(
            HttpStatusError,
            match=r"GET /users/999 failed with HTTP 404",
        ) as exc_info:
            retry_call(
                lambda: ensure_success(client.get("/users/999")),
                delay_s=0,
                retry_on=(ApiError,),
                retry_if = True,
            )

    assert attempts == 1

    assert isinstance(exc_info.value, HttpStatusError)
    assert isinstance(exc_info.value, ApiError)
    
    assert isinstance(
                exc_info.value,
                HttpStatusError,
            )
    
    assert str(exc_info.value) == 'GET /users/999 failed with HTTP 404: {"error":"Not found"}'
    assert exc_info.value.args[0] == 'GET /users/999 failed with HTTP 404: {"error":"Not found"}'
    assert str(exc_info.value) == 'GET /users/999 failed with HTTP 404: {"error":"Not found"}'
    assert exc_info.value.args == ('GET /users/999 failed with HTTP 404: {"error":"Not found"}',)
    assert exc_info.value.args[0] == 'GET /users/999 failed with HTTP 404: {"error":"Not found"}'
    assert str(exc_info.value) == exc_info.value.args[0]
    assert isinstance(
                                    exc_info.value,
                                    ApiError,
                                )
    assert issubclass(
                                    HttpStatusError,
                                    ApiError,
                                )
    
    assert isinstance(
                                    exc_info.value,
                                    HttpStatusError,
                                )
    
    assert isinstance(exc_info.value, ApiError)
    assert isinstance(exc_info.value, HttpStatusError)
    assert exc_info.type is HttpStatusError


@pytest.mark.api
def test_retry_does_not_retry_500_retry(settings):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        return httpx.Response(
            500,
            json={"error": "Not found"},
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(
            HttpStatusError,
            match=r"GET /users/999 failed with HTTP 500",
        ) as exc_info:
            retry_call(
                            lambda: ensure_success(client.get("/users/999")),
                            delay_s=0,
                            retry_on=(ApiError,),
                            retry_if = True,
                        )

    assert attempts == 1

    assert isinstance(exc_info.value, HttpStatusError)
    assert isinstance(exc_info.value, ApiError)
    
    assert isinstance(
                exc_info.value,
                HttpStatusError,
            )
    
    assert str(exc_info.value) == 'GET /users/999 failed with HTTP 500: {"error":"Not found"}'
    assert exc_info.value.args[0] == 'GET /users/999 failed with HTTP 500: {"error":"Not found"}'
    assert str(exc_info.value) == 'GET /users/999 failed with HTTP 500: {"error":"Not found"}'
    assert exc_info.value.args == ('GET /users/999 failed with HTTP 500: {"error":"Not found"}',)
    assert exc_info.value.args[0] == 'GET /users/999 failed with HTTP 500: {"error":"Not found"}'
    assert str(exc_info.value) == exc_info.value.args[0]
    assert isinstance(
                                    exc_info.value,
                                    ApiError,
                                )
    assert issubclass(
                                    HttpStatusError,
                                    ApiError,
                                )
    
    assert isinstance(
                                    exc_info.value,
                                    HttpStatusError,
                                )
    
    assert isinstance(exc_info.value, ApiError)
    assert isinstance(exc_info.value, HttpStatusError)
    assert exc_info.type is HttpStatusError

@pytest.mark.api
@pytest.mark.parametrize(
    "status",
    [429, 503],
    ids=[
        "too_many_requests",
        "service_unavailable",
    ],
)
def test_retry_retries_5xx_retry(settings, status):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        return httpx.Response(
            status,
            json={"error": "Not found"},
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(
            HttpStatusError,
            match=rf"GET /users/999 failed with HTTP {status}",
        ) as exc_info:
            retry_call(
                            lambda: ensure_success(client.get("/users/999")),
                            delay_s=0,
                            retry_on=(ApiError,),
                            retry_if = True,
                        )

    assert attempts == 3

    assert isinstance(exc_info.value, HttpStatusError)
    assert isinstance(exc_info.value, ApiError)
    
    assert isinstance(
                exc_info.value,
                HttpStatusError,
            )
    
    assert str(exc_info.value) == f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert exc_info.value.args[0] == f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert str(exc_info.value) == f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert exc_info.value.args == (f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}',)
    assert exc_info.value.args[0] == f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert str(exc_info.value) == exc_info.value.args[0]
    assert isinstance(
                                    exc_info.value,
                                    ApiError,
                                )
    assert issubclass(
                                    HttpStatusError,
                                    ApiError,
                                )
    
    assert isinstance(
                                    exc_info.value,
                                    HttpStatusError,
                                )
    
    assert isinstance(exc_info.value, ApiError)
    assert isinstance(exc_info.value, HttpStatusError)
    assert exc_info.type is HttpStatusError



@pytest.mark.api
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
def test_retry_no_retry_retry(settings, status):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        return httpx.Response(
            status,
            json={"error": "Not found"},
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(
            HttpStatusError,
            match=rf"GET /users/999 failed with HTTP {status}",
        ) as exc_info:
            retry_call(
                            lambda: ensure_success(client.get("/users/999")),
                            delay_s=0,
                            retry_on=(ApiError,),
                            retry_if = True,
                        )

    assert attempts == 1

    assert isinstance(exc_info.value, HttpStatusError)
    assert isinstance(exc_info.value, ApiError)
    
    assert isinstance(
                exc_info.value,
                HttpStatusError,
            )
    
    assert str(exc_info.value) == f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert exc_info.value.args[0] == f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert str(exc_info.value) == f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert exc_info.value.args == (f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}',)
    assert exc_info.value.args[0] == f'GET /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert str(exc_info.value) == exc_info.value.args[0]
    assert isinstance(
                                    exc_info.value,
                                    ApiError,
                                )
    assert issubclass(
                                    HttpStatusError,
                                    ApiError,
                                )
    
    assert isinstance(
                                    exc_info.value,
                                    HttpStatusError,
                                )
    
    assert isinstance(exc_info.value, ApiError)
    assert isinstance(exc_info.value, HttpStatusError)
    assert exc_info.type is HttpStatusError

@pytest.mark.parametrize(
    "error_type",
    [httpx.ConnectError, httpx.ReadTimeout],
    ids=[
        "connect_error",
        "read_timeout",
    ],
)
def test_retry_transport_error(settings, error_type):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise error_type(
            "transport failed",
            request=request,
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(
            ApiError,
            match=rf"GET /users failed: transport failed"
            ) as exc_info:
            retry_call(
                lambda: client.get("/users"),
                delay_s=0,
                retry_on=(ApiError,),
                retry_if = True,
            )

    assert attempts == 3
    assert isinstance(exc_info.value, ApiError)

    assert isinstance(
        exc_info.value.__cause__,
        error_type,
    )

    assert str(exc_info.value) == "GET /users failed: transport failed"
    assert exc_info.value.args[0] == "GET /users failed: transport failed"
    assert str(exc_info.value) == exc_info.value.args[0]
    assert exc_info.value.__cause__.request.url.path == "/users"
    assert exc_info.value.__cause__.request.method == "GET"
    assert str(exc_info.value.__cause__) == "transport failed"
    assert exc_info.value.__cause__.args == ("transport failed",)
    assert exc_info.value.__cause__.args[0] == "transport failed"
    assert str(exc_info.value.__cause__) == exc_info.value.__cause__.args[0]
    assert isinstance(
                            exc_info.value.__cause__,
                            httpx.HTTPError,
                        )
    assert issubclass(
                            error_type,
                            httpx.HTTPError,
                        )

    assert isinstance(
                            exc_info.value.__cause__,
                            error_type,
                        )

    assert isinstance(exc_info.value, ApiError)
    assert exc_info.type is ApiError

@pytest.mark.parametrize(
    "error_type",
    [httpx.ConnectError, httpx.ReadTimeout],
    ids=[
        "connect_error",
        "read_timeout",
    ],
)
def test_retry_transport_error_post(settings, error_type):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise error_type(
            "transport failed",
            request=request,
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(
            ApiError,
            match=rf"POST /users failed: transport failed"
            ) as exc_info:
            retry_call(
                lambda: client.post("/users"),
                delay_s=0,
                retry_on=(ApiError,),
                retry_if = True,
            )

    assert attempts == 1
    assert isinstance(exc_info.value, ApiError)

    assert isinstance(
        exc_info.value.__cause__,
        error_type,
    )

    assert str(exc_info.value) == "POST /users failed: transport failed"
    assert exc_info.value.args[0] == "POST /users failed: transport failed"
    assert str(exc_info.value) == exc_info.value.args[0]
    assert exc_info.value.__cause__.request.url.path == "/users"
    assert exc_info.value.__cause__.request.method == "POST"
    assert str(exc_info.value.__cause__) == "transport failed"
    assert exc_info.value.__cause__.args == ("transport failed",)
    assert exc_info.value.__cause__.args[0] == "transport failed"
    assert str(exc_info.value.__cause__) == exc_info.value.__cause__.args[0]
    assert isinstance(
                            exc_info.value.__cause__,
                            httpx.HTTPError,
                        )
    assert issubclass(
                            error_type,
                            httpx.HTTPError,
                        )

    assert isinstance(
                            exc_info.value.__cause__,
                            error_type,
                        )

    assert isinstance(exc_info.value, ApiError)
    assert exc_info.type is ApiError


@pytest.mark.api
@pytest.mark.parametrize(
    "status",
    [400, 401, 403, 404, 422, 500, 429, 503],
    ids=[
        "bad_request",
        "unauthorized",
        "forbidden",
        "not_found",
        "unprocessable_entity",
        "internal_server_error",
        "too_many_requests",
        "service_unavailable",
    ],
)
def test_retry_no_retry_retry_post(settings, status):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        return httpx.Response(
            status,
            json={"error": "Not found"},
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(
            HttpStatusError,
            match=rf"POST /users/999 failed with HTTP {status}",
        ) as exc_info:
            retry_call(
                            lambda: ensure_success(client.post("/users/999")),
                            delay_s=0,
                            retry_on=(ApiError,),
                            retry_if = True,
                        )

    assert attempts == 1

    assert isinstance(exc_info.value, HttpStatusError)
    assert isinstance(exc_info.value, ApiError)
    
    assert isinstance(
                exc_info.value,
                HttpStatusError,
            )
    
    assert str(exc_info.value) == f'POST /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert exc_info.value.args[0] == f'POST /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert str(exc_info.value) == f'POST /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert exc_info.value.args == (f'POST /users/999 failed with HTTP {status}: {{"error":"Not found"}}',)
    assert exc_info.value.args[0] == f'POST /users/999 failed with HTTP {status}: {{"error":"Not found"}}'
    assert str(exc_info.value) == exc_info.value.args[0]
    assert isinstance(
                                    exc_info.value,
                                    ApiError,
                                )
    assert issubclass(
                                    HttpStatusError,
                                    ApiError,
                                )
    
    assert isinstance(
                                    exc_info.value,
                                    HttpStatusError,
                                )
    
    assert isinstance(exc_info.value, ApiError)
    assert isinstance(exc_info.value, HttpStatusError)
    assert exc_info.type is HttpStatusError