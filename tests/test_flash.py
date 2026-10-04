import pytest
from lab_fw.ui.client import UIClient
from lab_fw.ui.pages.login_page import LoginPage
from lab_fw.ui.components.flash_message import FlashMessage
from unittest.mock import MagicMock, patch
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

@pytest.mark.ui
def test_is_visible(settings):
    with UIClient(settings) as ui:
        login_page = LoginPage(ui.page)
        login_page.open()

        secure_page = login_page.login(
            "tomsmith",
            "SuperSecretPassword!",
        )
        flash = FlashMessage(secure_page.page)
        assert flash.is_visible('You logged into a secure area!')
        login_page = secure_page.logout()
        flash = FlashMessage(login_page.page)
        assert flash.is_visible("You logged out of the secure area!")

@pytest.mark.ui
def test_no_is_visible(settings):
    with UIClient(settings) as ui:
        login_page = LoginPage(ui.page)
        login_page.open()

        secure_page = login_page.login(
            "tomsmith",
            "SuperSecretPassword!",
        )
        flash = FlashMessage(secure_page.page)
        assert not flash.is_visible('hello')

@pytest.mark.smoke
def test_flash_is_visible_uses_ui_timeout_ms():
    page = MagicMock()
    flash_loc = MagicMock()
    page.locator.return_value = flash_loc
    flash_loc.wait_for.side_effect = PlaywrightTimeoutError()
    with patch("lab_fw.ui.components.flash_message.ui_timeout_ms", return_value = 90_000):
        result = FlashMessage(page).is_visible("hello")

    assert not result
    assert result is False
    page.locator.assert_called_once_with("#flash")
    flash_loc.wait_for.assert_called_once_with(state="visible", timeout=90_000)
    