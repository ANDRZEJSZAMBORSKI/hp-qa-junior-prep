from playwright.sync_api import Page
from lab_fw.abstractions import BasePage

class LoginPage(BasePage):
    def __init__(self, page: Page):
        self.page = page
        self._username = self.page.get_by_label("Username")
        self._password = self.page.get_by_label("Password")
        self._login_button = self.page.get_by_role("button", name="Login")
        

    @property
    def path(self):
        return "/login"

    def open(self):
        self.page.goto(self.path)

    def is_username_visible(self):
        return self._username.is_visible()

    def is_password_visible(self):
        return self._password.is_visible()

    def get_url(self):
        return self.page.url

    def login(self, username: str, password: str):
        self._username.fill(username)
        self._password.fill(password)
        self._login_button.click()
        from lab_fw.ui.pages.secure_page import SecurePage

        return SecurePage(self.page)

    def is_login_success_message_visible(self, text: str):
        return self.page.get_by_text(text).is_visible()

    def is_login_error_message_visible(self, text: str):
        return self.page.get_by_text(text).is_visible()