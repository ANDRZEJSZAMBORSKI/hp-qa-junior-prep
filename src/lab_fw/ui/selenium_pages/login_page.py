from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from lab_fw.ui import BasePageSelenium
from lab_fw.ui.components.flash_message import FlashMessageSelenium
from lab_fw.ui.components.selenium_wait import SeleniumWait
from lab_fw.core.errors import UiError

class LoginPage(BasePageSelenium):
    def __init__(self, driver: WebDriver, base_url: str):
        super().__init__(driver, base_url)
        self.flash = FlashMessageSelenium(driver)
        self.wait = SeleniumWait(driver)
        self._username = (By.ID, "username")
        self._password = (By.ID, "password")
        self._login_button = (By.CSS_SELECTOR,'button[type="submit"]')
        
    @property
    def path(self):
        return "/login"

    def open(self) -> None:
        super().open()
        self.wait.visible(self._username)

    def get_username_visible(self) -> WebElement:
        return self.wait.visible(self._username)
                                                    
    def get_password_visible(self) -> WebElement:
        return self.wait.visible(self._password)
                                                
    def get_login_button_visible(self) -> WebElement:
        return self.wait.clickable(self._login_button)

    def is_username_visible(self) -> bool:
        return self.wait.is_visible(self._username)

    def is_password_visible(self) -> bool:
        return self.wait.is_visible(self._password)
        
    def is_login_button_visible(self) -> bool:
        return self.wait.is_clickable(self._login_button)
                                    
    def login(self, username: str, password: str):
        self.wait.visible(self._username).clear()
        self.wait.visible(self._username).send_keys(username)
        self.wait.visible(self._password).clear()
        self.wait.visible(self._password).send_keys(password)
        self.wait.clickable(self._login_button).click()
        self.wait.url_contains("/secure")                        
        from lab_fw.ui.selenium_pages.secure_page import SecurePage
        return SecurePage(self.driver, self.base_url)
        
    def is_login_success_message_visible(self, text: str) -> bool:
        return self.flash.is_visible(text)

    def is_logout_success_message_visible(self, text: str) -> bool:
        return self.flash.is_visible(text)

    def is_login_error_message_visible(self, text: str) -> bool:
        return self.flash.is_visible(text)

    def login_expect_failure(self, username: str, password: str) -> None:
        self.wait.visible(self._username).clear()
        self.wait.visible(self._username).send_keys(username)
        self.wait.visible(self._password).clear()
        self.wait.visible(self._password).send_keys(password)
        self.wait.clickable(self._login_button).click()
        try:
            WebDriverWait(self.driver, 3).until(EC.url_contains("/secure"))
        except TimeoutException:
            if "/login" not in self.driver.current_url:
                raise UiError(
                                    f"Expected /login after failed login (still at: {self.driver.current_url})"
                                )
            return

        raise UiError(
                            f"Login unexpectedly reached /secure (at: {self.driver.current_url})"
                        )