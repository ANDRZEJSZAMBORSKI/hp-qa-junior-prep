from unittest.mock import MagicMock, patch
import httpx
from lab_fw.api.client import ApiClient
from lab_fw.core.errors import ApiError
import pytest

@pytest.mark.mocks
@pytest.mark.mocks_pure
def test_patch():
    client = ApiClient()
    try:
        with patch.object(client._client, "request") as mock_request:  
            mock_request.return_value = httpx.Response(
                                                            200,
                                                            json = {"ok": True}
                                                        )
            response = client.get("/users")
            assert response.status_code == 200
            assert response.json() == {"ok": True}
            mock_request.assert_called_once_with("GET", "/users")
    finally:
        client.close()

@pytest.mark.mocks
@pytest.mark.mocks_pure
def test_patch_MagicMock():
    with ApiClient() as client:
        with patch.object(client._client, "request") as mock_request:  
            fake_response = MagicMock()
            fake_response.status_code = 200
            fake_response.json.return_value = {"ok": True}
            mock_request.return_value = fake_response
            response = client.get("/users")
            assert response.status_code == 200
            assert response.json() == {"ok": True}
            mock_request.assert_called_once_with("GET", "/users")

@pytest.mark.mocks
@pytest.mark.mocks_pure
def test_patch_mock_Client():
    with patch("lab_fw.api.client.httpx.Client") as mock_client:
        with ApiClient() as client:
            fake_response = MagicMock()
            fake_response.status_code = 200
            fake_response.json.return_value = {"ok": True}
            mock_client.return_value.request.return_value = fake_response
            response = client.get("/users")
            assert response.status_code == 200
            assert response.json() == {"ok": True}
            mock_client.assert_called_once_with(base_url = "https://example.com", timeout = 5.0)
            mock_client.return_value.request.assert_called_once_with("GET", "/users")

@pytest.mark.mocks
@pytest.mark.mocks_pure
def test_patch_request_connect_error():
    with ApiClient() as client:
        with patch.object(client._client, "request") as mock_request: 
            mock_request.side_effect = httpx.ConnectError("ConnectError: connection failed")
            with pytest.raises(ApiError, match=r"GET /users"):
                client.get("/users")
