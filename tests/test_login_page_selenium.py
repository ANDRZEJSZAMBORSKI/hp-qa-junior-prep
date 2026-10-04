import pytest

from lab_fw.ui.selenium_client import SeleniumClient
from lab_fw.ui.selenium_pages.login_page import LoginPage

@pytest.mark.selenium
def test_login_page_fields(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()
        assert login_page.get_url() == f"{settings.ui_base_url}/login"
        assert login_page.is_username_visible()
        assert login_page.is_password_visible()
        
@pytest.mark.selenium
def test_successful_login(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()
        assert login_page.get_url() == f"{settings.ui_base_url}/login"
        login_page.login("tomsmith", "SuperSecretPassword!")
        assert login_page.get_url() == f"{settings.ui_base_url}/secure"
        assert login_page.is_login_success_message_visible('You logged into a secure area!')

@pytest.mark.selenium
def test_successful_login_return_securepage(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()
        assert login_page.get_url() == f"{settings.ui_base_url}/login"
        securepage = login_page.login("tomsmith", "SuperSecretPassword!")
        assert login_page.get_url() == f"{settings.ui_base_url}/secure"
        assert login_page.is_login_success_message_visible('You logged into a secure area!')
        assert securepage.get_url() == f"{settings.ui_base_url}/secure"
        assert securepage.is_login_success_message_visible('You logged into a secure area!')

@pytest.mark.selenium
def test_login_page_fields_fixture(selenium_client):
    login_page = LoginPage(selenium_client.driver, selenium_client.settings.ui_base_url)
    login_page.open()
    assert login_page.get_url() == f"{selenium_client.settings.ui_base_url}/login"
    assert login_page.is_username_visible()
    assert login_page.is_password_visible()
        
@pytest.mark.selenium
def test_successful_login_fixture(selenium_client):
    login_page = LoginPage(selenium_client.driver, selenium_client.settings.ui_base_url)
    login_page.open()
    assert login_page.get_url() == f"{selenium_client.settings.ui_base_url}/login"
    login_page.login("tomsmith", "SuperSecretPassword!")
    assert login_page.get_url() == f"{selenium_client.settings.ui_base_url}/secure"
    assert login_page.is_login_success_message_visible('You logged into a secure area!')

@pytest.mark.selenium
def test_login_page_fields_fixture_module(selenium_client_module):
    """Opens /login; leaves the shared page on the login screen for the next test."""
    login_page = LoginPage(selenium_client_module.driver, selenium_client_module.settings.ui_base_url)
    login_page.open()

    assert login_page.get_url() == f"{selenium_client_module.settings.ui_base_url}/login"
    assert login_page.is_username_visible()
    assert login_page.is_password_visible()
        
@pytest.mark.selenium
def test_successful_login_fixture_module(selenium_client_module):
    """
    Intentionally no open(): same module-scoped page as the previous test.
    Checks shared state across tests, not isolation.
    Do not run this test alone — depends on test_login_page_fields_fixture_module.
    """
    login_page = LoginPage(selenium_client_module.driver, selenium_client_module.settings.ui_base_url)

    login_page.login("tomsmith", "SuperSecretPassword!")

    assert login_page.get_url() == f"{selenium_client_module.settings.ui_base_url}/secure"
    assert login_page.is_login_success_message_visible("You logged into a secure area!")

@pytest.mark.selenium
def test_open_waits_for_username(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, sc.settings.ui_base_url)
        login_page.open()
        assert login_page.is_username_visible()