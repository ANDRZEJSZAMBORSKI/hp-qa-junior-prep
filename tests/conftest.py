import pytest

from lab_fw.core.config import Settings, get_settings
from lab_fw.core.logging_setup import setup_logging


@pytest.fixture
def settings() -> Settings:
    return get_settings()


def pytest_configure(config):
    """Called once when pytest starts."""
    setup_logging(get_settings().log_level)

