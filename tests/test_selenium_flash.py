import pytest
from lab_fw.ui.selenium_client import SeleniumClient
from lab_fw.ui.selenium_pages.login_page import LoginPage
from lab_fw.ui.components.flash_message import FlashMessageSelenium

@pytest.mark.selenium
def test_flash_message_visible(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()
        secure_page = login_page.login(
                    "tomsmith",
                    "SuperSecretPassword!",
                )
        flash = FlashMessageSelenium(secure_page.driver)
        assert flash.is_visible('You logged into a secure area!')
        login_page = secure_page.logout()
        flash = FlashMessageSelenium(login_page.driver)
        assert flash.is_visible("You logged out of the secure area!")

@pytest.mark.selenium
def test_flash_message_not_visible(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()
        secure_page = login_page.login(
                    "tomsmith",
                    "SuperSecretPassword!",
                )
        flash = FlashMessageSelenium(secure_page.driver)
        assert not flash.is_visible('hello')

@pytest.mark.selenium
def test_xpath_literal():
    flash = FlashMessageSelenium(None)
    assert flash._xpath_literal("hello") == "'hello'"
    assert flash._xpath_literal("hello'world") == '"hello\'world"'
    assert flash._xpath_literal('hello"world\'test') == "concat('hello\"world', \"'\", 'test')"