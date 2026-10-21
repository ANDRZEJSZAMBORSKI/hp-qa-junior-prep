import pytest

from lab_fw.core.config import get_settings
from lab_fw.core.errors import ConfigError
from lab_fw.ui.selenium_client import SeleniumClient
from unittest.mock import patch

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

@pytest.mark.config
def test_settings_selenium_remote_url_from_env(monkeypatch):
    monkeypatch.setenv("SELENIUM_REMOTE_URL", "http://localhost:4444")
    settings = get_settings()
    assert settings.selenium_remote_url == "http://localhost:4444"

@pytest.mark.config
def test_selenium_client_preserves_timeout_error_when_quit_fails(monkeypatch):
    # Verify that the original timeout error is preserved when driver cleanup also fails.
    monkeypatch.delenv("SELENIUM_REMOTE_URL", raising=False)
    settings = get_settings()
    with (
          patch("lab_fw.ui.selenium_client.webdriver.Chrome") as mock_Chrome,  
        ):
        mock_Chrome.return_value.set_page_load_timeout.side_effect = RuntimeError("timeout setup failed")
        mock_Chrome.return_value.quit.side_effect = RuntimeError("quit failed")
        with pytest.raises(RuntimeError, match="timeout setup failed"):
            with SeleniumClient(settings) as sc:
                pass
        mock_Chrome.assert_called_once()
        mock_Chrome.return_value.quit.assert_called_once()

@pytest.mark.config
def test_settings_selenium_remote_url_missing(monkeypatch):
    # Verify that a missing Grid URL selects local Chrome.
    monkeypatch.delenv("SELENIUM_REMOTE_URL", raising=False)

    settings = get_settings()

    assert settings.selenium_remote_url is None

@pytest.mark.config
def test_settings_selenium_remote_url_whitespace(monkeypatch):
    # Verify that a whitespace-only Grid URL is treated as missing.
    monkeypatch.setenv("SELENIUM_REMOTE_URL", "   ")

    settings = get_settings()

    assert settings.selenium_remote_url is None