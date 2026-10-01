import pytest
from lab_fw.core.errors import UiError
from lab_fw.ui.selenium_client import SeleniumClient
from lab_fw.ui.selenium_pages.login_page import LoginPage
from lab_fw.ui.selenium_pages.secure_page import SecurePage
import re
from selenium.common.exceptions import TimeoutException

@pytest.mark.selenium
def test_secure_page_after_login(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()

        secure_page = login_page.login(
            "tomsmith",
            "SuperSecretPassword!",
        )
        assert login_page.is_login_success_message_visible("You logged into a secure area!")
        assert secure_page.get_url() == f"{settings.ui_base_url}/secure"
        assert secure_page.is_logout_success_message_visible(
            "You logged into a secure area!"
        )


@pytest.mark.selenium
def test_secure_page_logout(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()

        secure_page = login_page.login(
            "tomsmith",
            "SuperSecretPassword!",
        )
        assert login_page.is_login_success_message_visible('You logged into a secure area!')
        login_page = secure_page.logout()
        assert secure_page.is_logout_success_message_visible("You logged out of the secure area!")
        assert login_page.is_login_success_message_visible("You logged out of the secure area!")
        assert login_page.get_url() == f"{settings.ui_base_url}/login"
        assert login_page.is_username_visible()
        assert login_page.is_password_visible()
        
@pytest.mark.selenium
def test_login_with_invalid_password(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()
        with pytest.raises(
                        UiError, match=rf"Login did not navigate to /secure \(still at: {re.escape(login_page.driver.current_url)}\)"
                           ) as exc_info:
            login_page.login("tomsmith", "WrongPassword!")

        assert login_page.get_url() == f"{settings.ui_base_url}/login"
        assert login_page.is_login_error_message_visible(
            "Your password is invalid!"
        )
  
        assert isinstance(exc_info.value, UiError)
        
        assert str(exc_info.value) == f"Login did not navigate to /secure (still at: {login_page.driver.current_url})"
        assert exc_info.value.args[0] == f"Login did not navigate to /secure (still at: {login_page.driver.current_url})"
        assert exc_info.value.args == (f"Login did not navigate to /secure (still at: {login_page.driver.current_url})",)
        assert str(exc_info.value) == exc_info.value.args[0]
        
        assert isinstance(exc_info.value.__cause__, TimeoutException)
        assert exc_info.type is UiError


@pytest.mark.selenium
def test_login_with_invalid_username(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()
        with pytest.raises(
                        UiError, match=rf"Login did not navigate to /secure \(still at: {re.escape(login_page.driver.current_url)}\)"
                           ) as exc_info:
        
            login_page.login("wrong_user", "SuperSecretPassword!",)

        assert login_page.get_url() == f"{settings.ui_base_url}/login"
        assert login_page.is_login_error_message_visible(
            "Your username is invalid!"
        )

        assert isinstance(exc_info.value, UiError)
        
        assert str(exc_info.value) == f"Login did not navigate to /secure (still at: {login_page.driver.current_url})"
        assert exc_info.value.args[0] == f"Login did not navigate to /secure (still at: {login_page.driver.current_url})"
        assert exc_info.value.args == (f"Login did not navigate to /secure (still at: {login_page.driver.current_url})",)
        assert str(exc_info.value) == exc_info.value.args[0]
        
        assert isinstance(exc_info.value.__cause__, TimeoutException)
        assert exc_info.type 

@pytest.mark.selenium
def test_login_logout_login_again(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()

        secure_page = login_page.login(
            "tomsmith",
            "SuperSecretPassword!",
        )

        assert secure_page.get_url() == f"{settings.ui_base_url}/secure"

        login_page = secure_page.logout()

        assert login_page.get_url() == f"{settings.ui_base_url}/login"
        assert login_page.is_username_visible()
        assert login_page.is_password_visible()

        secure_page = login_page.login(
            "tomsmith",
            "SuperSecretPassword!",
        )

        assert secure_page.get_url() == f"{settings.ui_base_url}/secure"
        assert secure_page.is_logout_success_message_visible(
            "You logged into a secure area!"
        )


@pytest.mark.selenium
def test_secure_page_after_login_fixture(selenium_client):
    login_page = LoginPage(selenium_client.driver, selenium_client.settings.ui_base_url)
    login_page.open()

    secure_page = login_page.login(
        "tomsmith",
        "SuperSecretPassword!",
    )

    assert login_page.is_login_success_message_visible(
        "You logged into a secure area!"
    )
    assert secure_page.get_url() == f"{selenium_client.settings.ui_base_url}/secure"
    assert secure_page.is_logout_success_message_visible(
        "You logged into a secure area!"
    )


@pytest.mark.selenium
def test_secure_page_logout_fixture(selenium_client):
    login_page = LoginPage(selenium_client.driver, selenium_client.settings.ui_base_url)
    login_page.open()

    secure_page = login_page.login(
        "tomsmith",
        "SuperSecretPassword!",
    )

    assert login_page.is_login_success_message_visible(
        "You logged into a secure area!"
    )

    login_page = secure_page.logout()

    assert secure_page.is_logout_success_message_visible(
        "You logged out of the secure area!"
    )
    assert login_page.is_login_success_message_visible(
        "You logged out of the secure area!"
    )
    assert login_page.get_url() == f"{selenium_client.settings.ui_base_url}/login"
    assert login_page.is_username_visible()
    assert login_page.is_password_visible()


@pytest.mark.selenium
def test_secure_page_after_login_fixture_module(selenium_client_module):
    """
    Opens /login and logs in.
    Leaves the shared page on /secure for the next test.
    """
    login_page = LoginPage(selenium_client_module.driver, selenium_client_module.settings.ui_base_url)
    login_page.open()

    secure_page = login_page.login(
        "tomsmith",
        "SuperSecretPassword!",
    )

    assert login_page.is_login_success_message_visible(
        "You logged into a secure area!"
    )
    assert secure_page.get_url() == f"{selenium_client_module.settings.ui_base_url}/secure"
    assert secure_page.is_logout_success_message_visible(
        "You logged into a secure area!"
    )


@pytest.mark.selenium
def test_secure_page_logout_fixture_module(selenium_client_module):
    """
    Intentionally no open() or login().
    Uses the same module-scoped page left on /secure
    by the previous test.
    Do not run this test alone.
    """
    secure_page = SecurePage(selenium_client_module.driver, selenium_client_module.settings.ui_base_url)

    assert secure_page.get_url() == f"{selenium_client_module.settings.ui_base_url}/secure"

    login_page = secure_page.logout()

    assert secure_page.is_logout_success_message_visible(
        "You logged out of the secure area!"
    )
    assert login_page.is_login_success_message_visible(
        "You logged out of the secure area!"
    )
    assert login_page.get_url() == f"{selenium_client_module.settings.ui_base_url}/login"
    assert login_page.is_username_visible()
    assert login_page.is_password_visible()

@pytest.mark.selenium
def test_login_again_without_logout(settings):
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()

        login_page.login(
            "tomsmith",
            "SuperSecretPassword!",
        )

        login_page = LoginPage(sc.driver, settings.ui_base_url)

        login_page.open()

        secure_page = login_page.login(
            "tomsmith",
            "SuperSecretPassword!",
        )

        assert secure_page.get_url() == f"{settings.ui_base_url}/secure"


@pytest.mark.selenium
def test_login_with_new_browser_session(settings):
    # First browser session
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()

        secure_page = login_page.login(
            "tomsmith",
            "SuperSecretPassword!",
        )

        assert secure_page.get_url() == f"{settings.ui_base_url}/secure"

    # Second browser session
    with SeleniumClient(settings) as sc:
        login_page = LoginPage(sc.driver, settings.ui_base_url)
        login_page.open()

        secure_page = login_page.login(
            "tomsmith",
            "SuperSecretPassword!",
        )

        assert secure_page.get_url() == f"{settings.ui_base_url}/secure"