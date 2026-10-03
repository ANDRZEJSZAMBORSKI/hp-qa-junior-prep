from playwright.sync_api import Page
from selenium.webdriver.remote.webdriver import WebDriver
from lab_fw.abstractions import BasePage as AbstractBasePage
from lab_fw.ui.timeouts import ui_timeout_ms

class BasePage(AbstractBasePage):
    def __init__(self, page: Page):
        self.page = page

    def open(self) -> None:
        self.page.goto(self.path, wait_until="domcontentloaded", timeout=ui_timeout_ms())

    def get_url(self) -> str:
        return self.page.url

class BasePageSelenium(AbstractBasePage):
    def __init__(self, driver: WebDriver, base_url: str):
        self.driver = driver
        self.base_url = base_url
    
    def open(self) -> None:
        self.driver.get(f"{self.base_url}{self.path}")

    def get_url(self) -> str:
        return self.driver.current_url