import pytest
from lab_fw.ui.selenium_client import SeleniumClient
from lab_fw.ui.selenium_pages.login_page import LoginPage
from lab_fw.ui.components.flash_message import FlashMessageSelenium
from unittest.mock import MagicMock, patch
from selenium.common.exceptions import TimeoutException

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


@pytest.mark.smoke
def test_flash_is_visible_uses_ui_timeout_s():
    driver = MagicMock()
    with patch(
                "lab_fw.ui.components.flash_message.ui_timeout_s", return_value = 90.0
               ), patch("lab_fw.ui.components.flash_message.WebDriverWait"
               ) as wdw, patch("lab_fw.ui.components.flash_message.EC"
               ) as ec, patch("lab_fw.ui.components.flash_message.By") as by:
        by.XPATH = "xpath"
        ec.visibility_of_element_located.return_value = MagicMock()
        wdw.return_value.until.side_effect = TimeoutException()
        result = FlashMessageSelenium(driver).is_visible("hello")

    assert not result
    assert result is False
    wdw.assert_called_once_with(driver, 90.0)
    ec.visibility_of_element_located.assert_called_once_with(("xpath", f"//*[contains(text(), 'hello')]"))

  