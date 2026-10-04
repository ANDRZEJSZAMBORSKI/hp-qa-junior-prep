import pytest

from lab_fw.ui.client import UIClient
from lab_fw.ui.pages.login_page import LoginPage

@pytest.mark.ui
def test_login_page_fields(settings):
    with UIClient(settings) as ui:
        login_page = LoginPage(ui.page)
        login_page.open()
        assert login_page.get_url() == f"{settings.ui_base_url}/login"
        assert login_page.is_username_visible()
        assert login_page.is_password_visible()
        
@pytest.mark.ui
def test_successful_login(settings):
    with UIClient(settings) as ui:
        login_page = LoginPage(ui.page)
        login_page.open()
        assert login_page.get_url() == f"{settings.ui_base_url}/login"
        login_page.login("tomsmith", "SuperSecretPassword!")
        assert login_page.get_url() == f"{settings.ui_base_url}/secure"
        assert login_page.is_login_success_message_visible('You logged into a secure area!')

@pytest.mark.ui
def test_successful_login_return_securepage(settings):
    with UIClient(settings) as ui:
        login_page = LoginPage(ui.page)
        login_page.open()
        assert login_page.get_url() == f"{settings.ui_base_url}/login"
        securepage = login_page.login("tomsmith", "SuperSecretPassword!")
        assert login_page.get_url() == f"{settings.ui_base_url}/secure"
        assert login_page.is_login_success_message_visible('You logged into a secure area!')
        assert securepage.get_url() == f"{settings.ui_base_url}/secure"
        assert securepage.is_login_success_message_visible('You logged into a secure area!')

@pytest.mark.ui
def test_login_page_fields_fixture(ui_client):
    login_page = LoginPage(ui_client.page)
    login_page.open()
    assert login_page.get_url() == f"{ui_client.settings.ui_base_url}/login"
    assert login_page.is_username_visible()
    assert login_page.is_password_visible()
        
@pytest.mark.ui
def test_successful_login_fixture(ui_client):
    login_page = LoginPage(ui_client.page)
    login_page.open()
    assert login_page.get_url() == f"{ui_client.settings.ui_base_url}/login"
    login_page.login("tomsmith", "SuperSecretPassword!")
    assert login_page.get_url() == f"{ui_client.settings.ui_base_url}/secure"
    assert login_page.is_login_success_message_visible('You logged into a secure area!')

@pytest.mark.ui
def test_login_page_fields_fixture_module(ui_client_module):
    """Opens /login; leaves the shared page on the login screen for the next test."""
    login_page = LoginPage(ui_client_module.page)
    login_page.open()

    assert login_page.get_url() == f"{ui_client_module.settings.ui_base_url}/login"
    assert login_page.is_username_visible()
    assert login_page.is_password_visible()
        
@pytest.mark.ui
def test_successful_login_fixture_module(ui_client_module):
    """
    Intentionally no open(): same module-scoped page as the previous test.
    Checks shared state across tests, not isolation.
    Do not run this test alone — depends on test_login_page_fields_fixture_module.
    """
    login_page = LoginPage(ui_client_module.page)

    login_page.login("tomsmith", "SuperSecretPassword!")

    assert login_page.get_url() == f"{ui_client_module.settings.ui_base_url}/secure"
    assert login_page.is_login_success_message_visible("You logged into a secure area!")