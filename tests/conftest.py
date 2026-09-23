import logging

import pytest

from lab_fw.core.config import Settings, get_settings
from lab_fw.core.logging_setup import setup_logging


@pytest.fixture
def settings() -> Settings:
    return get_settings()


def pytest_configure(config):
    """Called once when pytest starts."""
    setup_logging(get_settings().log_level)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """After pytest builds the test report, log failures."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        logging.getLogger("lab_fw.pytest").error(
            "FAILED %s: %s",
            item.nodeid,
            report.longrepr,
        )