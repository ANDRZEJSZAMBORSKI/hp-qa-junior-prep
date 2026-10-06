import httpx
import pytest
from lab_fw.api.client import ApiClient
from lab_fw.core.config import Settings

@pytest.mark.compose
def test_mock_api_users():
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

@pytest.mark.compose
def test_mock_api_is_reachable():
    response = httpx.get("http://mock-api:1080")

    assert response.status_code < 500