import pytest
import httpx
from lab_fw.core.config import Settings, get_settings
from lab_fw.core.logging_setup import setup_logging
from lab_fw.api.client import ApiClient
from lab_fw.ui.client import UIClient
from lab_fw.ui.selenium_client import SeleniumClient
import os
import platform
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import shutil

@pytest.fixture
def settings() -> Settings:
    return get_settings()


def pytest_configure(config):
    """Called once when pytest starts."""
    setup_logging(get_settings().log_level)

    # Only the main pytest process should write Allure metadata.
    if hasattr(config, "workerinput"):
        return

    results_dir = config.getoption("allure_report_dir", default=None)
    if not results_dir:
        return

    results_path = Path(results_dir)
    results_path.mkdir(parents=True, exist_ok=True)

    categories_source = Path(config.rootpath) / "categories.json"
    if categories_source.is_file():
        shutil.copy2(categories_source, results_path / "categories.json")

    try:
        pytest_version = version("pytest")
    except PackageNotFoundError:
        pytest_version = "not installed"

    try:
        allure_version = version("allure-pytest")
    except PackageNotFoundError:
        allure_version = "not installed"

    if os.getenv("GITHUB_ACTIONS", "").lower() == "true":
        execution_environment = "GitHub Actions"
    elif Path("/.dockerenv").exists():
        execution_environment = "Docker"
    else:
        execution_environment = "Local"

    properties = {
        "Project": "hp-qa-junior-prep",
        "Test framework": f"pytest {pytest_version}",
        "Reporting": f"Allure (allure-pytest {allure_version})",
        "Operating system": platform.platform(),
        "Python version": sys.version.split()[0],
        "Execution environment": execution_environment,
    }

    environment_file = results_path / "environment.properties"
    environment_file.write_text(
        "".join(f"{key}={value}\n" for key, value in properties.items()),
        encoding="utf-8",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    """Compose tests share one MockServer; serialize them under xdist loadgroup."""
    for item in items:
        if item.get_closest_marker("compose") is not None:
            item.add_marker(pytest.mark.xdist_group(name="mockserver"))

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

@pytest.fixture
def selenium_client(settings):
    sc = SeleniumClient(settings)
    sc.start()
    yield sc
    sc.close()

@pytest.fixture(scope="module")
def selenium_client_module(module_settings):
    sc = SeleniumClient(module_settings)
    sc.start()
    yield sc
    sc.close()

