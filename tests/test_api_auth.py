import httpx
import pytest
from lab_fw.api.client import ApiClient
from lab_fw.core.config import Settings
from lab_fw.api.auth import fetch_client_credentials_token
from lab_fw.core.errors import ApiError
from urllib.parse import parse_qs

@pytest.mark.api
def test_api_token_adds_bearer_header():
    captured_request = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json={"ok": True})

    settings = Settings(
        base_url="https://example.com",
        timeout_s=5.0,
        log_level="INFO",
        api_token="tok-123",
    )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        response = client.get("/users")

    assert response.status_code == 200
    assert captured_request.headers["Authorization"] == "Bearer tok-123"


@pytest.mark.api
def test_api_token_none_does_not_add_bearer_header():
    captured_request = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json={"ok": True})

    settings = Settings(
        base_url="https://example.com",
        timeout_s=5.0,
        log_level="INFO",
    )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        response = client.get("/users")

    assert response.status_code == 200
    assert "Authorization" not in captured_request.headers

@pytest.mark.api
def test_fetch_client_credentials_token():
    requests = []
    responses = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/oauth/token":
            response = httpx.Response(
                200,
                json={
                    "access_token": "tok-123",
                    "token_type": "bearer",
                    "expires_in": 3600,
                },
            )
            responses.append(response)
            return response
        if request.url.path == "/users":
            response = httpx.Response(200, json={"ok": True})
            responses.append(response)
            return response

    settings = Settings(
        base_url="https://example.com",
        timeout_s=5.0,
        log_level="INFO",
    )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        token = fetch_client_credentials_token(client, "client-1", "secret-1")
        response = client.get("/users")
        form = parse_qs(requests[0].content.decode())
        assert form == {
                        "grant_type": ["client_credentials"],
                        "client_id": ["client-1"],
                        "client_secret": ["secret-1"],
                    }   
        assert requests[0].url.path == "/oauth/token"
        assert requests[1].url.path == "/users"
        assert requests[0].method == "POST"
        assert requests[1].method == "GET"
        assert client._client._transport is transport
        assert requests[0].url.host == "example.com"
        assert requests[1].url.host == "example.com"
        assert str(requests[0].url) == "https://example.com/oauth/token"
        assert str(requests[1].url) == "https://example.com/users"
        assert client._client.timeout.connect == 5.0
        assert client._client.base_url == "https://example.com"                
        assert "Authorization" not in requests[0].headers
        assert "Authorization" in requests[1].headers
        assert "Authorization" in client._client.headers
        assert client._client.headers["Authorization"] == "Bearer tok-123"
        assert requests[1].headers["Authorization"] == "Bearer tok-123"
        assert token == "tok-123"
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        token_response = responses[0]
        assert token_response.status_code == 200
        assert token_response.json() == {
            "access_token": "tok-123",
            "token_type": "bearer",
            "expires_in": 3600,
        }
        token_response = responses[1]
        assert token_response.status_code == 200
        assert token_response.json() == {"ok": True}
        assert "Authorization" not in responses[0].request.headers
        assert responses[1].request.headers["Authorization"] == "Bearer tok-123"

@pytest.mark.api
def test_fetch_client_negative_OAuth_case():
    requests = []
    responses = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/oauth/token":
            response = httpx.Response(
                401,
                json={"error": "invalid_client"},
            )
            responses.append(response)
            return response
        if request.url.path == "/users":
            response = httpx.Response(200, json={"ok": True})
            responses.append(response)
            return response

    settings = Settings(
        base_url="https://example.com",
        timeout_s=5.0,
        log_level="INFO",
    )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        with pytest.raises(ApiError, match="OAuth token request failed: HTTP 401",):
            token = fetch_client_credentials_token(client, "client-1", "secret-1")
        assert "token" not in locals()
        assert len(requests) == 1
        response = client.get("/users")
        assert len(requests) == 2
        assert requests[0].url.path == "/oauth/token"
        assert requests[1].url.path == "/users"
        assert requests[0].method == "POST"
        assert requests[1].method == "GET"
        assert client._client._transport is transport
        assert requests[0].url.host == "example.com"
        assert requests[1].url.host == "example.com"
        assert str(requests[0].url) == "https://example.com/oauth/token"
        assert str(requests[1].url) == "https://example.com/users"
        assert client._client.timeout.connect == 5.0
        assert client._client.base_url == "https://example.com"                
        assert "Authorization" not in requests[0].headers
        assert "Authorization" not in requests[1].headers
        assert "Authorization" not in client._client.headers
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        token_response = responses[0]
        assert token_response.status_code == 401
        assert token_response.json() == {"error": "invalid_client"}
        token_response = responses[1]
        assert token_response.status_code == 200
        assert token_response.json() == {"ok": True}
        assert "Authorization" not in responses[0].request.headers
        assert "Authorization" not in responses[1].request.headers
              