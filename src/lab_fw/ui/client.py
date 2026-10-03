from playwright.sync_api import Browser, BrowserContext, Page
from playwright.sync_api import Playwright, sync_playwright

from lab_fw.core.errors import UiError
from lab_fw.core.config import Settings
from lab_fw.ui.timeouts import ui_timeout_ms

class UIClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        
    @property
    def settings(self) -> Settings:
        return self._settings

    @settings.setter
    def settings(self, value: Settings):
        if not value.ui_base_url:
            raise UiError("LAB_FW_UI_BASE_URL cannot be empty.")
        self._settings = value

    @property
    def playwright(self) -> Playwright:
        if self._playwright is None:
            raise UiError("UI client is not started.")
        return self._playwright

    @property
    def browser(self) -> Browser:
        if self._browser is None:
            raise UiError("UI client is not started.")
        return self._browser

    @property 
    def context(self) -> BrowserContext:
        if self._context is None:
            raise UiError("UI client is not started.")
        return self._context

    @property
    def page(self) -> Page:
        if self._page is None:
            raise UiError("UI client is not started.")
        return self._page

    def start(self):
        ms = ui_timeout_ms()
        self._playwright = sync_playwright().start()
        self._browser = self.playwright.chromium.launch()
        self._context = self.browser.new_context(base_url=self.settings.ui_base_url)
        self._page = self.context.new_page()
        self._page.set_default_navigation_timeout(ms)
        self._page.set_default_timeout(ms)

    def __enter__(self):
        self.start()
        return self

    def close(self) -> None:
        if self._context:
            self._context.close()
        if self._browser: 
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        self._context = None
        self._browser = None
        self._playwright = None
        self._page = None

    def __exit__(self, exc_type, exc, tb):
        self.close()