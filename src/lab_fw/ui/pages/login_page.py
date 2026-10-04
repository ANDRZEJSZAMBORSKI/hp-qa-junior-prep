from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from lab_fw.ui import BasePage
from lab_fw.ui.components.flash_message import FlashMessage
from lab_fw.ui.components.playwright_wait import PlaywrightWait
from lab_fw.core.errors import UiError

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.flash = FlashMessage(page)
        self.wait = PlaywrightWait(page)
        #self._username = self.page.get_by_label("Username")
        #self._password = self.page.get_by_label("Password")
        #self._login_button = self.page.get_by_role("button", name="Login")
        self._username = self.page.locator("#username")
        self._password = self.page.locator("#password")
        self._login_button = self.page.locator("button[type='submit']")
        
    @property
    def path(self):
        return "/login"

    def open(self) -> None:
        super().open()
        self.wait.wait_visible(self._username)

    def is_username_visible(self):
        return self.wait.is_visible(self._username)

    def is_password_visible(self):
        return self.wait.is_visible(self._password)

    def login(self, username: str, password: str):
        self.wait.wait_visible(self._username).fill(username)
        self._password.fill(password)
        self._login_button.click()
        self.wait.wait_url("**/secure")
        from lab_fw.ui.pages.secure_page import SecurePage
        return SecurePage(self.page)

    def is_login_success_message_visible(self, text: str):
        return self.flash.is_visible(text)

    def is_login_error_message_visible(self, text: str):
        return self.flash.is_visible(text)

    def is_logout_success_message_visible(self, text: str):
        return self.flash.is_visible(text)

    def login_expect_failure(self, username: str, password: str) -> None:
        self.wait.wait_visible(self._username).fill(username)
        self._password.fill(password)
        self._login_button.click()
        try:
            self.page.wait_for_url("**/secure", timeout=3_000)
        except PlaywrightTimeoutError:
            if "/login" not in self.page.url:
                raise UiError(
                                    f"Expected /login after failed login (still at: {self.page.url})"
                                )
            return

        raise UiError(
                            f"Login unexpectedly reached /secure (at: {self.page.url})"
                        )