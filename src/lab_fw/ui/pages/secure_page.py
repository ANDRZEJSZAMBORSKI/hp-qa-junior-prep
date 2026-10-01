from playwright.sync_api import Page
from lab_fw.abstractions import BasePage


class SecurePage(BasePage):
    def __init__(self, page: Page):
        self.page = page
        self._logout_button = self.page.get_by_role("link", name="Logout")

    @property
    def path(self):
        return "/secure"

    def open(self):
        self.page.goto(self.path)

    def get_url(self):
        return self.page.url

    def logout(self):
        self._logout_button.click()
        from lab_fw.ui.pages.login_page import LoginPage

        return LoginPage(self.page)
    
    def is_logout_success_message_visible(self, text: str):
        return self.page.get_by_text(text).is_visible()