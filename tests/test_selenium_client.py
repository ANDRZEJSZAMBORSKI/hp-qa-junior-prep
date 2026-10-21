import pytest
from lab_fw.ui.selenium_client import SeleniumClient
from lab_fw.core.config import get_settings, Settings
from lab_fw.core.errors import ConfigError
from unittest.mock import patch
from lab_fw.ui.timeouts import ui_timeout_s


def _require_selenium_grid(settings) -> None:
    """Live Grid tests: need SELENIUM_REMOTE_URL (CI sets http://selenium:4444)."""
    if settings.selenium_remote_url is None:
        pytest.skip(
            "Set SELENIUM_REMOTE_URL (e.g. http://localhost:4444 with Grid up) "
            "to run live Grid tests."
        )

@pytest.mark.selenium
def test_selenium_client_uses_local_chrome_without_remote_url(monkeypatch):
    monkeypatch.delenv("SELENIUM_REMOTE_URL", raising=False)
    settings = get_settings()
    assert settings.selenium_remote_url is None
    with (
          patch("lab_fw.ui.selenium_client.webdriver.Chrome") as mock_Chrome,  
          patch("lab_fw.ui.selenium_client.webdriver.Remote") as mock_Remote
        ):
        with SeleniumClient(settings) as sc:
            mock_Chrome.assert_called_once()
            mock_Remote.assert_not_called()
            mock_Chrome.return_value.set_page_load_timeout.assert_called_once_with(ui_timeout_s())

@pytest.mark.selenium
def test_selenium_client_uses_remote_grid_when_url_is_configured(monkeypatch):
    # Verify that SeleniumClient uses the configured Grid URL instead of local Chrome.
    monkeypatch.setenv("SELENIUM_REMOTE_URL", "http://localhost:4444")
    settings = get_settings()
    assert settings.selenium_remote_url == "http://localhost:4444"
    with (
          patch("lab_fw.ui.selenium_client.webdriver.Chrome") as mock_Chrome,  
          patch("lab_fw.ui.selenium_client.webdriver.Remote") as mock_Remote
        ):
        with SeleniumClient(settings) as sc:
            mock_Remote.assert_called_once()
            mock_Chrome.assert_not_called()
            mock_Remote.return_value.set_page_load_timeout.assert_called_once_with(ui_timeout_s())
            mock_Remote.assert_called_once_with(
                                                    command_executor="http://localhost:4444",
                                                    options=mock_Remote.call_args.kwargs["options"],
                                                )
            assert mock_Remote.call_args.kwargs["command_executor"] == "http://localhost:4444"
            assert "options" in mock_Remote.call_args.kwargs            
            options = mock_Remote.call_args.kwargs["options"]

            assert options.arguments == [
                                            "--disable-features=PasswordLeakDetection",
                                        ]

            assert options.experimental_options["prefs"] == {
                                                                "credentials_enable_service": False,
                                                                "profile.password_manager_enabled": False,
                                                                "profile.password_manager_leak_detection": False,
                                                            }


@pytest.mark.selenium
def test_selenium_client_connects_to_real_grid(settings, monkeypatch):
    if settings.selenium_remote_url is None:
        monkeypatch.setenv("SELENIUM_REMOTE_URL", "http://localhost:4444")
    settings = get_settings()
    with SeleniumClient(settings) as sc:
        assert sc.driver is not None
        capabilities = sc.driver.capabilities
        assert capabilities["browserName"].lower() == "chrome"
        assert capabilities["platformName"].lower() == "linux"

@pytest.mark.selenium
def test_selenium_client_connects_to_real_grid_2(settings, selenium_client):
    # Verify that a real browser session can connect to Selenium Grid.
    _require_selenium_grid(settings)
    assert selenium_client.driver is not None
    assert selenium_client.driver.capabilities["browserName"] == "chrome"
    assert selenium_client.driver.capabilities["platformName"] == "linux"