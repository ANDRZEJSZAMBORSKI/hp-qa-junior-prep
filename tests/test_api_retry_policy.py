import httpx
import pytest

from lab_fw.api.retry_policy import should_retry
from lab_fw.core.errors import ApiError, HttpStatusError
from lab_fw.api.client import ApiClient, ensure_success
from lab_fw.core.retry import retry_call

@pytest.mark.parametrize(
    "status",
    [429, 503],
    ids=["too_many_requests", "service_unavailable"],
)
def test_should_retry_get_retryable_status(status):
    request = httpx.Request("GET", "http://test/users")

    response = httpx.Response(
        status,
        request=request,
    )

    exc = HttpStatusError(
        f"GET /users failed with HTTP {status}",
        response=response,
    )

    assert should_retry(exc) is True


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
def test_should_not_retry_get_non_retryable_status(status):
    request = httpx.Request("GET", "http://test/users")

    response = httpx.Response(
        status,
        request=request,
    )

    exc = HttpStatusError(
        f"GET /users failed with HTTP {status}",
        response=response,
    )

    assert should_retry(exc) is False


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
def test_should_retry_get_transport_error(error_type):
    request = httpx.Request("GET", "http://test/users")
    cause = error_type("transport failed", request=request)

    exc = ApiError(
        "GET /users failed: transport failed"
    )
    exc.__cause__ = cause

    assert should_retry(exc) is True


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
def test_should_not_retry_post_transport_error(error_type):
    request = httpx.Request("POST", "http://test/users")
    cause = error_type("transport failed", request=request)

    exc = ApiError(
        "POST /users failed: transport failed"
    )
    exc.__cause__ = cause

    assert should_retry(exc) is False


@pytest.mark.parametrize(
    "status",
    [429, 503],
    ids=["too_many_requests", "service_unavailable"],
)
def test_should_not_retry_post_status(status):
    request = httpx.Request("POST", "http://test/users")

    response = httpx.Response(
        status,
        request=request,
    )

    exc = HttpStatusError(
        f"POST /users failed with HTTP {status}",
        response=response,
    )

    assert should_retry(exc) is False


def test_should_not_retry_api_error_without_http_cause():
    exc = ApiError("unknown API error")

    assert should_retry(exc) is False


def test_should_not_retry_http_status_error_without_response():
    exc = HttpStatusError(
        "invalid status error",
        response=None,
    )

    assert should_retry(exc) is False


@pytest.mark.api
def test_get_retries_transport_error_then_succeeds(settings):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            raise httpx.ConnectError("transport failed", request=request,)
        return httpx.Response (200, request=request, json={"id": 1, "name": "John"})

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        response = retry_call(
                    lambda: client.get("/users/999"),
                    delay_s=0,
                    retry_on=(ApiError,),
                    retry_if = True,
                                )

    assert attempts == 3
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "John"}

@pytest.mark.api
def test_get_retries_503_then_succeeds(settings):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            return httpx.Response(503, request=request)

        return httpx.Response(
            200,
            request=request,
            json={"ok": True},
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        response = retry_call(
            lambda: ensure_success(client.get("/users/999")),
            attempts=3,
            delay_s=0,
            retry_on=(ApiError,),
            retry_if = True,
        )

    assert attempts == 3
    assert response.status_code == 200
    assert response.json() == {"ok": True}

@pytest.mark.api
def test_post_does_not_retry_transport_error(settings):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            raise httpx.ConnectError("transport failed", request=request,)
        return httpx.Response (200, request=request, json={"id": 1, "name": "John"})

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(ApiError):
            retry_call(
                    lambda: client.post("/users/999"),
                    delay_s=0,
                    retry_on=(ApiError,),
                    retry_if = True,
                                )

    assert attempts == 1

@pytest.mark.api
def test_post_does_not_retry_503(settings):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            return httpx.Response(503, request=request)

        return httpx.Response(
            200,
            request=request,
            json={"ok": True},
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(HttpStatusError):
            retry_call(
                lambda: ensure_success(client.post("/users/999")),
                attempts=3,
                delay_s=0,
                retry_on=(ApiError,),
                retry_if = True,
            )

    assert attempts == 1

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
        with pytest.raises(HttpStatusError):
            retry_call(
                lambda: ensure_success(client.get("/users/999")),
                attempts=3,
                delay_s=0,
                retry_on=(ApiError,),
                retry_if = True,
            )

    assert attempts == 1


@pytest.mark.api
@pytest.mark.parametrize(
    "status",
    [429, 503],
    ids=[
        "too_many_requests",
        "service_unavailable",
    ],
)
@pytest.mark.api
def test_get_retry_exhausted(settings, status):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        return httpx.Response(status, request=request)

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(HttpStatusError):
            retry_call(
                lambda: ensure_success(client.get("/users/999")),
                attempts=3,
                delay_s=0,
                retry_on=(ApiError,),
                retry_if = True,
            )

    assert attempts == 3