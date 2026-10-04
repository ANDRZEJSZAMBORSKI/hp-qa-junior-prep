import pytest

from lab_fw.core.errors import UiError
from lab_fw.ui.client import UIClient
from lab_fw.ui.components.playwright_wait import PlaywrightWait
from lab_fw.ui.pages.login_page import LoginPage
from lab_fw.ui.timeouts import ui_timeout_ms


@pytest.mark.ui
def test_wait_visible(settings):
    with UIClient(settings) as ui:
        login_page = LoginPage(ui.page)
        login_page.open()
        wait = PlaywrightWait(ui.page)
        locator = wait.wait_visible(login_page._username)
        assert locator.is_visible()


@pytest.mark.ui
def test_wait_visible_timeout(settings):
    with UIClient(settings) as ui:
        login_page = LoginPage(ui.page)
        login_page.open()
        wait = PlaywrightWait(ui.page, timeout=1_000)
        with pytest.raises(UiError, match="failed to become visible"):
            wait.wait_visible(ui.page.locator("#hello"))


@pytest.mark.ui
def test_is_visible(settings):
    with UIClient(settings) as ui:
        login_page = LoginPage(ui.page)
        login_page.open()
        wait = PlaywrightWait(ui.page)
        assert wait.is_visible(login_page._username)
        assert wait.is_visible(login_page._password)


@pytest.mark.ui
def test_no_is_visible(settings):
    with UIClient(settings) as ui:
        login_page = LoginPage(ui.page)
        login_page.open()
        wait = PlaywrightWait(ui.page, timeout=1_000)
        assert not wait.is_visible(ui.page.locator("#hello"))


@pytest.mark.ui
def test_wait_url(settings):
    with UIClient(settings) as ui:
        login_page = LoginPage(ui.page)
        login_page.open()
        wait = PlaywrightWait(ui.page)
        wait.wait_url("**/login")
        assert "/login" in ui.page.url


@pytest.mark.ui
def test_wait_url_timeout(settings):
    with UIClient(settings) as ui:
        login_page = LoginPage(ui.page)
        login_page.open()
        wait = PlaywrightWait(ui.page, timeout=1_000)
        with pytest.raises(UiError, match="URL did not match"):
            wait.wait_url("**/no-such-path")


@pytest.mark.ui
def test_playwright_wait_default_timeout(settings):
    with UIClient(settings) as ui:
        wait = PlaywrightWait(ui.page)
        assert wait.timeout == ui_timeout_ms()

@pytest.mark.ui
def test_wait_visible_timeout_wrong_locator(settings):
    with UIClient(settings) as ui:
        ui.page.goto("/login", wait_until="domcontentloaded", timeout=ui_timeout_ms())
        wait = PlaywrightWait(ui.page, timeout=1_000)
        with pytest.raises(UiError, match="failed to become visible"):
            wait.wait_visible(ui.page.locator("#hello"))

@pytest.mark.ui
def test_is_visible_timeout_wrong_locator(settings):
    with UIClient(settings) as ui:
        ui.page.goto("/login", wait_until="domcontentloaded", timeout=ui_timeout_ms())
        wait = PlaywrightWait(ui.page, timeout=1_000)
        assert not wait.is_visible(ui.page.locator("#hello"))

@pytest.mark.ui
def test_wait_url_timeout_wrong_url(settings):
    with UIClient(settings) as ui:
        ui.page.goto("/login", wait_until="domcontentloaded", timeout=ui_timeout_ms())
        wait = PlaywrightWait(ui.page, timeout=1_000)
        with pytest.raises(UiError, match="URL did not match"):
            wait.wait_url("**/hello")

            