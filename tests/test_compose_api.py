import httpx
import pytest
from lab_fw.api.client import ApiClient
from lab_fw.core.config import Settings

@pytest.fixture
def reset_mockserver():
    url = "http://mock-api:1080/mockserver/reset"

    response = httpx.put(url)
    assert response.status_code == 200

    yield

    response = httpx.put(url)
    assert response.status_code == 200

@pytest.mark.compose
def test_mock_api_users(reset_mockserver):
    response = httpx.put(
        "http://mock-api:1080/mockserver/expectation",
        json={
            "httpRequest": {
                "method": "GET",
                "path": "/users/1",
            },
            "httpResponse": {
                "statusCode": 200,
                "headers": {
                    "Content-Type": ["application/json"],
                },
                "body": {
                    "id": 1,
                    "name": "Alice",
                },
            },
        },
    )

    assert response.status_code == 201

    settings = Settings(
        base_url="http://mock-api:1080",
        timeout_s=5.0,
        log_level="INFO",
    )

    with ApiClient(settings) as client:
        response = client.get("/users/1")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Alice"}
    assert "application/json" in response.headers["content-type"].lower()

    verify_response = httpx.put(
        "http://mock-api:1080/mockserver/verify",
        json={
            "httpRequest": {
                "method": "GET",
                "path": "/users/1",
            },
            "times": {
                "atLeast": 1,
            },
        },
    )

    assert verify_response.status_code == 202

@pytest.mark.compose
def test_mock_api_is_reachable():
    response = httpx.get("http://mock-api:1080")

    assert response.status_code < 500