import pytest

from lab_fw.core.config import Settings, get_settings


@pytest.fixture
def settings() -> Settings:
    return get_settings()