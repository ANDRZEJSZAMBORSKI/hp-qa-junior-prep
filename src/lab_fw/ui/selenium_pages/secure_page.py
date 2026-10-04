from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from lab_fw.ui import BasePageSelenium
from lab_fw.ui.components.flash_message import FlashMessageSelenium
from lab_fw.ui.components.selenium_wait import SeleniumWait

class SecurePage(BasePageSelenium):
    def __init__(self, driver: WebDriver, base_url: str):
        super().__init__(driver, base_url)
        self.flash = FlashMessageSelenium(driver)
        self.wait = SeleniumWait(driver)
        self._logout_button = (By.CSS_SELECTOR, "a.button.secondary.radius")
        
    @property
    def path(self):
        return "/secure"

    def get_logout_button_visible(self) -> WebElement:
        return self.wait.clickable(self._logout_button)
                                        
    def is_logout_button_visible(self) -> bool:
        return self.wait.is_clickable(self._logout_button)

    def logout(self):
        self.wait.clickable(self._logout_button).click()
        self.wait.url_contains("/login")
        from lab_fw.ui.selenium_pages.login_page import LoginPage
        return LoginPage(self.driver, self.base_url)

    def is_login_success_message_visible(self, text: str) -> bool:
        return self.flash.is_visible(text)

    def is_logout_success_message_visible(self, text: str) -> bool:
        return self.flash.is_visible(text)

    def is_login_error_message_visible(self, text: str) -> bool:
        return self.flash.is_visible(text)