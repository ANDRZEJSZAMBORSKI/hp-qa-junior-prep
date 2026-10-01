import pytest
import httpx
from lab_fw.core.config import Settings, get_settings
from lab_fw.core.logging_setup import setup_logging
from lab_fw.api.client import ApiClient
from lab_fw.ui.client import UIClient


@pytest.fixture
def settings() -> Settings:
    return get_settings()


def pytest_configure(config):
    """Called once when pytest starts."""
    setup_logging(get_settings().log_level)

@pytest.fixture
def api_client(settings):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)

    client = ApiClient(settings, transport=transport)
    yield client
    client.close()

@pytest.fixture(scope="module")
def module_settings() -> Settings:
    return get_settings()

@pytest.fixture(scope="module")
def module_settings_id(module_settings):
    return id(module_settings)

@pytest.fixture
def ui_client(settings):
    ui = UIClient(settings)
    ui.start()
    yield ui
    ui.close()

@pytest.fixture(scope="module")
def ui_client_module(module_settings):
    ui = UIClient(module_settings)
    ui.start()
    yield ui
    ui.close()

