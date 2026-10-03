from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from lab_fw.ui.timeouts import ui_timeout_ms, ui_timeout_s 

class FlashMessage:
    def __init__(self, page: Page):
        self.page = page

    def is_visible_(self, text: str) -> bool:
        locator = self.page.get_by_text(text)
        try:
            locator.wait_for(state="visible", timeout=ui_timeout_ms())
            return True
        except PlaywrightTimeoutError:
            return False

    def is_visible(self, text: str) -> bool:
        flash = self.page.locator("#flash")
        try:
            flash.wait_for(state="visible", timeout=ui_timeout_ms())
            return text in (flash.inner_text() or "")
        except PlaywrightTimeoutError:
            return False

class FlashMessageSelenium:
    def __init__(self, driver: WebDriver):
        self.driver = driver
    
    def _xpath_literal(self, text: str) -> str:
        if "'" not in text:
            return f"'{text}'"

        if '"' not in text:
            return f'"{text}"'

        parts = text.split("'")
        return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"

    def is_visible(self, text: str) -> bool:
        text = self._xpath_literal(text)
        try:
            return WebDriverWait(self.driver, ui_timeout_s()).until(
                EC.visibility_of_element_located(
                    (By.XPATH, f"//*[contains(text(), {text})]")
                )
            ).is_displayed()
        
        except TimeoutException:
            return False
