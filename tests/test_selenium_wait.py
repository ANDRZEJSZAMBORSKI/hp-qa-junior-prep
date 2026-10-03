import pytest
from lab_fw.ui.selenium_client import SeleniumClient
from lab_fw.ui.selenium_pages.login_page import LoginPage
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from lab_fw.ui.components.selenium_wait import SeleniumWait
from selenium.webdriver.remote.webelement import WebElement
from lab_fw.core.errors import UiError
from lab_fw.ui.timeouts import ui_timeout_s

@pytest.mark.selenium
def test_visible(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()
        wait = SeleniumWait(login_page.driver)
        element = wait.visible(login_page._username)
        assert isinstance(element, WebElement)
        assert element.is_displayed()
        element = wait.visible(login_page._password)
        assert isinstance(element, WebElement)
        assert element.is_displayed()

@pytest.mark.selenium
def test_clickable(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()
        wait = SeleniumWait(login_page.driver)
        element = wait.clickable(login_page._login_button)
        assert isinstance(element, WebElement)
        assert element.is_displayed()

@pytest.mark.selenium
def test_no_visible(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()
        wait = SeleniumWait(login_page.driver, timeout=1)
        with pytest.raises(UiError):
            wait.visible((By.ID, "hello"))

@pytest.mark.selenium
def test_no_clickable(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()
        wait = SeleniumWait(login_page.driver, timeout=1)
        with pytest.raises(UiError):
            wait.clickable((By.CSS_SELECTOR, 'button[type="hello"]'))
        
@pytest.mark.selenium
def test_is_visible(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()
        wait = SeleniumWait(login_page.driver)
        assert wait.is_visible(login_page._username)
        assert wait.is_visible(login_page._password)

@pytest.mark.selenium
def test_is_clickable(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()
        wait = SeleniumWait(login_page.driver)
        assert wait.is_clickable(login_page._login_button)
       
@pytest.mark.selenium
def test_no_is_visible(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()
        wait = SeleniumWait(login_page.driver, timeout=1)
        assert not wait.is_visible((By.ID, "hello"))

@pytest.mark.selenium
def test_no_is_clickable(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()
        wait = SeleniumWait(login_page.driver, timeout=1)
        assert not wait.is_clickable((By.CSS_SELECTOR, 'button[type="hello"]'))

@pytest.mark.selenium
def test_url_contains(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()
        wait = SeleniumWait(login_page.driver)
        wait.url_contains("/login")
        assert "/login" in login_page.get_url()

@pytest.mark.selenium
def test_url_contains_timeout(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()
        wait = SeleniumWait(login_page.driver, timeout=1)
        with pytest.raises(UiError, match="URL did not contain"):
            wait.url_contains("/no-such-path")

@pytest.mark.selenium
def test_selenium_wait_default_timeout(settings):
    with SeleniumClient(settings) as sc:
        wait = SeleniumWait(sc.driver)
        assert wait.timeout == ui_timeout_s()