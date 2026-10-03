from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from lab_fw.ui.timeouts import ui_timeout_s
from lab_fw.core.errors import UiError

class SeleniumWait:
    def __init__(self, driver: WebDriver, timeout: float | None = None):
        self.driver = driver
        self.timeout = ui_timeout_s() if timeout is None else timeout
 
    def visible(self, locator: tuple[str, str]) -> WebElement:
        try:
            return WebDriverWait(self.driver, self.timeout).until(
                                                            EC.visibility_of_element_located(locator)
                                                        )
        except TimeoutException as e:
            raise UiError(
                                f"Element {locator!r} failed to become visible"
                            ) from e

    def clickable(self, locator: tuple[str, str]) -> WebElement:
        try:
            return WebDriverWait(self.driver, self.timeout).until(
                                                            EC.element_to_be_clickable(locator)
                                                        )
        except TimeoutException as e:
            raise UiError(
                                f"Element {locator!r} failed to become clickable"
                            ) from e

    def is_visible(self, locator: tuple[str, str]) -> bool:
        try:
            return self.visible(locator).is_displayed()
        except UiError:
            return False

    def is_clickable(self, locator: tuple[str, str]) -> bool:
        try:
            return self.clickable(locator).is_displayed()
        except UiError:
            return False

    def url_contains(self, path: str):
        try:
            WebDriverWait(self.driver, self.timeout).until(
                                                    EC.url_contains(path)
                                                )
        except TimeoutException as e:
            raise UiError(
                            f"URL did not contain {path!r} (still at: {self.driver.current_url})"
                        ) from e