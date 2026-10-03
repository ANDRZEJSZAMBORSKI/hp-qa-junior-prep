from playwright.sync_api import Page
from playwright.sync_api import Locator
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from lab_fw.core.errors import UiError
from lab_fw.ui.timeouts import ui_timeout_ms

class PlaywrightWait:
    def __init__(self, page: Page, timeout: float | None = None):
        self.page = page
        self.timeout = ui_timeout_ms() if timeout is None else timeout

    def is_visible(self, locator: Locator) -> bool:
        try:
            locator.wait_for(state="visible", timeout=self.timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def wait_visible(self, locator: Locator):
        try:
            locator.wait_for(state="visible", timeout=self.timeout)
            return locator
        except PlaywrightTimeoutError as e:
            raise UiError(f'The element "{locator}" failed to become visible') from e

    def wait_url(self, url: str) -> None:
        try:
            self.page.wait_for_url(url, timeout=self.timeout)
        except PlaywrightTimeoutError as e:
            raise UiError(
                f"URL did not match {url!r} (still at: {self.page.url})"
            ) from e