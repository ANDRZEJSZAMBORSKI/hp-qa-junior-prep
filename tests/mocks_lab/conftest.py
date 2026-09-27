import httpx
import pytest

@pytest.fixture
def mock_handler():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"source": "mocks_lab"})

    return handler