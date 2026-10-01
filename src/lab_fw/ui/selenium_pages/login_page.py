from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from lab_fw.abstractions import BasePage
from lab_fw.core.errors import UiError

class LoginPage(BasePage):
    def __init__(self, driver: WebDriver, base_url: str):
        self.driver = driver
        self.base_url = base_url
        
        self._username = (By.ID, "username")
        self._password = (By.ID, "password")
        self._login_button = (By.CSS_SELECTOR,'button[type="submit"]')
        

    @property
    def path(self):
        return "/login"

    def open(self):
        self.driver.get(f"{self.base_url}{self.path}")

    def get_username_visible(self):
        return WebDriverWait(self.driver, 10).until(
                                                        EC.visibility_of_element_located(self._username)
                                                    )

    def get_password_visible(self):
        return WebDriverWait(self.driver, 10).until(
                                                        EC.visibility_of_element_located(self._password)
                                                    )

    def get_login_button_visible(self):
        return WebDriverWait(self.driver, 10).until(
                                                        EC.element_to_be_clickable(self._login_button)
                                                    )

    def is_username_visible(self):
        try:
            return WebDriverWait(self.driver, 10).until(
                                                            EC.visibility_of_element_located(self._username)
                                                        ).is_displayed()
        except TimeoutException:
            return False    

    def is_password_visible(self):
        try:
            return WebDriverWait(self.driver, 10).until(
                                                            EC.visibility_of_element_located(self._password)
                                                        ).is_displayed()
        except TimeoutException:
            return False

    def is_login_button_visible(self):
        try:
            return WebDriverWait(self.driver, 10).until(
                                                            EC.element_to_be_clickable(self._login_button)
                                                        ).is_displayed()
        except TimeoutException:
            return False

    def get_url(self):
        return self.driver.current_url

    def login(self, username: str, password: str):
        self.get_username_visible().clear()
        self.get_username_visible().send_keys(username)
        self.get_password_visible().clear()
        self.get_password_visible().send_keys(password)
        self.get_login_button_visible().click()
        
        try:
            WebDriverWait(self.driver, 10).until(
                                                    EC.url_contains("/secure")
                                                )

            from lab_fw.ui.selenium_pages.secure_page import SecurePage

            return SecurePage(self.driver, self.base_url)
        except TimeoutException as e:
            raise UiError(
                            f"Login did not navigate to /secure (still at: {self.driver.current_url})"
                        ) from e

    def _xpath_literal(self, text: str) -> str:
        if "'" not in text:
            return f"'{text}'"

        if '"' not in text:
            return f'"{text}"'

        parts = text.split("'")
        return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"

    def is_login_success_message_visible(self, text: str):
        text = self._xpath_literal(text)
        try:
            return WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, f"//*[contains(text(), {text})]")
                )
            ).is_displayed()
        
        except TimeoutException:
            return False

    def is_login_error_message_visible(self, text: str):
        text = self._xpath_literal(text)
        try:
            return WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, f"//*[contains(text(), {text})]")
                )
            ).is_displayed()
        
        except TimeoutException:
            return False