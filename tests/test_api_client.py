import httpx
import pytest

from lab_fw.api.client import ApiClient
from lab_fw.core.config import Settings
from lab_fw.core.errors import ApiError
from lab_fw.reporting import feature
from lab_fw.reporting import severity
from lab_fw.reporting import SeverityLevel

@feature("API Client")
def test_get_ok_with_mock_transport():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/users"
        return httpx.Response(200, json={"items": [1, 2]})

    settings = Settings(
        base_url="https://example.com",
        timeout_s=2.0,
        log_level="INFO",
    )
    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        response = client.get("/users")

    assert response.status_code == 200
    assert response.json() == {"items": [1, 2]}

@feature("API Client")
@severity(SeverityLevel.CRITICAL)
def test_request_http_error_becomes_api_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no network", request=request)

    settings = Settings(
        base_url="https://example.com",
        timeout_s=2.0,
        log_level="INFO",
    )
    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(ApiError):
            client.get("/users")