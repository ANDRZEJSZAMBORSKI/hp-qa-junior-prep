import pytest

from lab_fw.core.config import get_settings
from lab_fw.core.errors import ConfigError


def test_settings_defaults(settings):
    assert settings.base_url == "https://example.com"
    assert settings.timeout_s == 5.0
    assert settings.log_level == "INFO"


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("LAB_FW_BASE_URL", "https://staging.example.com")
    monkeypatch.setenv("LAB_FW_TIMEOUT_S", "2.5")
    s = get_settings()
    assert s.base_url == "https://staging.example.com"
    assert s.timeout_s == 2.5


def test_settings_bad_timeout(monkeypatch):
    monkeypatch.setenv("LAB_FW_TIMEOUT_S", "abc")
    with pytest.raises(ConfigError):
        get_settings()