from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from lab_fw.abstractions import BasePage
from lab_fw.core.errors import UiError


class SecurePage(BasePage):
    def __init__(self, driver: WebDriver, base_url: str):
        self.driver = driver
        self.base_url = base_url

        self._logout_button = (By.CSS_SELECTOR, "a.button.secondary.radius")
        

    @property
    def path(self):
        return "/secure"

    def open(self):
        self.driver.get(f"{self.base_url}{self.path}")

    def get_logout_button_visible(self):
        return WebDriverWait(self.driver, 10).until(
                                                        EC.element_to_be_clickable(self._logout_button)
                                                    )

    def is_logout_button_visible(self):
        try:
            return WebDriverWait(self.driver, 10).until(
                                                            EC.element_to_be_clickable(self._logout_button)
                                                        ).is_displayed()
        except TimeoutException:
            return False

    def get_url(self):
        return self.driver.current_url

    def logout(self):
        self.get_logout_button_visible().click()
        try:
            WebDriverWait(self.driver, 10).until(
                                                    EC.url_contains("/login")
                                                )

            from lab_fw.ui.selenium_pages.login_page import LoginPage

            return LoginPage(self.driver, self.base_url)
        except TimeoutException as e:
            raise UiError(
                f"Logout did not navigate to /login (still at: {self.driver.current_url})"
            ) from e

    def _xpath_literal(self, text: str) -> str:
        if "'" not in text:
            return f"'{text}'"

        if '"' not in text:
            return f'"{text}"'

        parts = text.split("'")
        return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"

    def is_logout_success_message_visible(self, text: str):
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