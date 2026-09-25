from unittest.mock import Mock
from lab_fw.api.client import ApiClient
import pytest

@pytest.mark.smoke
@pytest.mark.mocks
def test_mock_get_fake():
    client = Mock()
    client.get.return_value = "fake"
    assert client.get() == "fake"

def make_user(name: str, role: str) -> dict:
    return {
        "name": name,
        "role": role,
    }
@pytest.mark.smoke
@pytest.mark.mocks
def test_spy_wraps():
    spy = Mock(wraps=make_user)
    result = spy("Alice", role="admin")
    assert result == {
        "name": "Alice",
        "role": "admin",
    }
    spy.assert_called_once_with("Alice", role="admin")

@pytest.mark.smoke
@pytest.mark.mocks
def test_api_monkeypatch(monkeypatch):
    def fake_get(self, path):
        return "fake response"
    monkeypatch.setattr(ApiClient, "get", fake_get)
    with ApiClient() as client:
        assert client.get("/users") == "fake response"
