import pytest

from lab_fw.core.config import get_settings
from lab_fw.core.errors import ConfigError

@pytest.mark.config
@pytest.mark.smoke
def test_settings_defaults(settings):
    assert settings.base_url == "https://example.com"
    assert settings.timeout_s == 5.0
    assert settings.log_level == "INFO"
    assert settings.ui_timeout_s == 120.0

@pytest.mark.config
def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("LAB_FW_BASE_URL", "https://staging.example.com")
    monkeypatch.setenv("LAB_FW_TIMEOUT_S", "2.5")
    monkeypatch.setenv("LAB_FW_UI_TIMEOUT_S", "90")
    s = get_settings()
    assert s.base_url == "https://staging.example.com"
    assert s.timeout_s == 2.5
    assert s.ui_timeout_s == 90.0

@pytest.mark.config
def test_settings_bad_timeout(monkeypatch):
    monkeypatch.setenv("LAB_FW_TIMEOUT_S", "abc")
    with pytest.raises(ConfigError):
        get_settings()

@pytest.mark.config
def test_settings_bad_ui_timeout(monkeypatch):
    monkeypatch.setenv("LAB_FW_UI_TIMEOUT_S", "abc")
    with pytest.raises(ConfigError):
        get_settings()

@pytest.mark.config
def test_settings_ui_timeout_not_positive(monkeypatch):
    monkeypatch.setenv("LAB_FW_UI_TIMEOUT_S", "0")
    with pytest.raises(ConfigError):
        get_settings()

    monkeypatch.setenv("LAB_FW_UI_TIMEOUT_S", "-1")
    with pytest.raises(ConfigError):
        get_settings()