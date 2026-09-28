import pytest
import httpx
from lab_fw.api.schemas import User, TokenResponse, parse_user, parse_token
from lab_fw.core.errors import SchemaError
from lab_fw.api.client import ApiClient
from urllib.parse import parse_qs

@pytest.mark.api
def test_parse_user_valid():
    data = {
        "id": 1,
        "name": "John",
    }

    user = parse_user(data)

    assert isinstance(user, User)
    assert user.id == 1
    assert user.name == "John"
    assert user.model_dump() == {
                                    "id": 1,
                                    "name": "John",

                                }
@pytest.mark.api
def test_parse_token_valid():
    data = {
        "access_token": "tok-123",
        "token_type": "bearer",
        "expires_in": 3600,
    }

    token = parse_token(data)

    assert isinstance(token, TokenResponse)
    assert token.access_token == "tok-123"
    assert token.token_type == "bearer"
    assert token.expires_in == 3600
    assert token.model_dump() == {
                                    "access_token": "tok-123",
                                    "token_type": "bearer",
                                    "expires_in": 3600,
                                }

@pytest.mark.api
def test_parse_user_wrong_type():
    data = {
        "id": "1",
        "name": "John",
    }

    with pytest.raises(SchemaError, match="User schema validation failed"):
        parse_user(data)

@pytest.mark.api
def test_parse_user_missing_field():
    data = {
        "id": 1,
    }

    with pytest.raises(SchemaError, match="User schema validation failed"):
        parse_user(data)

@pytest.mark.api
def test_parse_user_extra_field():
    data = {
        "id": 1,
        "name": "John",
        "email": "john@example.com",
    }

    with pytest.raises(SchemaError, match="User schema validation failed"):
        parse_user(data)

@pytest.mark.api
def test_parse_token_missing_field():
    data = {
        "access_token": "tok-123",
        "token_type": "bearer",
    }

    with pytest.raises(
                            SchemaError,
                            match="TokenResponse schema validation failed",
                        ):
        parse_token(data)

@pytest.mark.api
def test_parse_token_wrong_type():
    data = {
        "access_token": "tok-123",
        "token_type": "bearer",
        "expires_in": "3600",
    }

    with pytest.raises(
                            SchemaError,
                            match="TokenResponse schema validation failed",
                        ):
        parse_token(data)

@pytest.mark.api
def test_parse_token_extra_field():
    data = {
        "access_token": "tok-123",
        "token_type": "bearer",
        "expires_in": 3600,
        "scope": "read",
    }

    with pytest.raises(
                            SchemaError,
                            match="TokenResponse schema validation failed",
                        ):
        parse_token(data)

@pytest.mark.api
def test_mock_transport_parse_user(settings):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/users/1"

        return httpx.Response(
            200,
            json={
                "id": 1,
                "name": "John",
            },
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        response = client.get("/users/1")

    user = parse_user(response.json())

    assert isinstance(user, User)
    assert user.id == 1
    assert user.name == "John"
    assert user.model_dump() == {
                                    "id": 1,
                                    "name": "John",
                                }
    assert response.status_code == 200
    assert response.json() == {
                                    "id": 1,
                                    "name": "John",
                                }
    assert client._client.timeout.connect == 5.0
    assert client._client.base_url == "https://example.com" 
    assert response.request.url.path == "/users/1"
    assert response.request.url.host == "example.com"
    assert response.request.method == "GET"

@pytest.mark.api
def test_mock_transport_parse_token(settings):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/oauth/token"

        return httpx.Response(
            200,
            json={
                "access_token": "tok-123",
                "token_type": "bearer",
                "expires_in": 3600,
            },
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        response = client.post(
            "/oauth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": "client-1",
                "client_secret": "secret-1",
            },
        )

    token_response = parse_token(response.json())

    assert isinstance(token_response, TokenResponse)
    assert token_response.access_token == "tok-123"
    assert token_response.token_type == "bearer"
    assert token_response.expires_in == 3600
    assert token_response.model_dump() == {
                                                "access_token": "tok-123",
                                                "token_type": "bearer",
                                                "expires_in": 3600,
                                            }
    assert response.status_code == 200
    assert response.json() == {
                                    "access_token": "tok-123",
                                    "token_type": "bearer",
                                    "expires_in": 3600,
                                }
    assert client._client.timeout.connect == 5.0
    assert client._client.base_url == "https://example.com" 
    assert response.request.url.path == "/oauth/token"
    assert response.request.url.host == "example.com"
    assert response.request.method == "POST"
    form = parse_qs(response.request.content.decode())
    assert form == {
                            "grant_type": ["client_credentials"],
                            "client_id": ["client-1"],
                            "client_secret": ["secret-1"],
                        }     

@pytest.mark.api
def test_mock_transport_parse_user_invalid(settings):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "wrong",
                "name": "John",
            },
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        response = client.get("/users/1")

    with pytest.raises(SchemaError, match="User schema validation failed"):
        parse_user(response.json())
