import pytest
from lab_fw.ui.client import UIClient
from lab_fw.ui.pages.login_page import LoginPage
from lab_fw.ui.pages.secure_page import SecurePage
from lab_fw.ui.components.flash_message import FlashMessage

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