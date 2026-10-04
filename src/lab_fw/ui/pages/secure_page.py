from playwright.sync_api import Page
from lab_fw.ui import BasePage
from lab_fw.ui.components.flash_message import FlashMessage
from lab_fw.ui.components.playwright_wait import PlaywrightWait

class SecurePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.flash = FlashMessage(page)
        self.wait = PlaywrightWait(page)
        #self._logout_button = self.page.get_by_role("link", name="Logout")
        self._logout_button = self.page.locator('a[href="/logout"]')

    @property
    def path(self):
        return "/secure"

    def logout(self):
        self.wait.wait_visible(self._logout_button).click()
        self.wait.wait_url("**/login")
        from lab_fw.ui.pages.login_page import LoginPage
        return LoginPage(self.page)
        
    def is_login_success_message_visible(self, text: str):
        return self.flash.is_visible(text)

    def is_logout_success_message_visible(self, text: str):
        return self.flash.is_visible(text)