
import pytest

from lab_fw.ui.client import UIClient
from lab_fw.ui.pages.login_page import LoginPage
from lab_fw.ui.pages.secure_page import SecurePage
from lab_fw.core.errors import UiError

@pytest.mark.ui
def test_secure_page_after_login(settings):
    with UIClient(settings) as ui:
        login_page = LoginPage(ui.page)
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


@pytest.mark.ui
def test_secure_page_logout(settings):
    with UIClient(settings) as ui:
        login_page = LoginPage(ui.page)
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
        
@pytest.mark.ui
def test_login_with_invalid_password(settings):
    with UIClient(settings) as ui:
        login_page = LoginPage(ui.page)
        login_page.open()

        with pytest.raises(UiError, match="URL did not match"):
            login_page.login("tomsmith", "WrongPassword!")

        assert login_page.get_url() == f"{settings.ui_base_url}/login"
        assert login_page.is_login_error_message_visible(
            "Your password is invalid!"
        )

@pytest.mark.ui
def test_login_with_invalid_username(settings):
    with UIClient(settings) as ui:
        login_page = LoginPage(ui.page)
        login_page.open()

        with pytest.raises(UiError, match="URL did not match"):
            login_page.login(
                "wrong_user",
                "SuperSecretPassword!",
            )

        assert login_page.get_url() == f"{settings.ui_base_url}/login"
        assert login_page.is_login_error_message_visible(
            "Your username is invalid!"
        )

@pytest.mark.ui
def test_login_logout_login_again(settings):
    with UIClient(settings) as ui:
        login_page = LoginPage(ui.page)
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


@pytest.mark.ui
def test_secure_page_after_login_fixture(ui_client):
    login_page = LoginPage(ui_client.page)
    login_page.open()

    secure_page = login_page.login(
        "tomsmith",
        "SuperSecretPassword!",
    )

    assert login_page.is_login_success_message_visible(
        "You logged into a secure area!"
    )
    assert secure_page.get_url() == f"{ui_client.settings.ui_base_url}/secure"
    assert secure_page.is_logout_success_message_visible(
        "You logged into a secure area!"
    )


@pytest.mark.ui
def test_secure_page_logout_fixture(ui_client):
    login_page = LoginPage(ui_client.page)
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
    assert login_page.get_url() == f"{ui_client.settings.ui_base_url}/login"
    assert login_page.is_username_visible()
    assert login_page.is_password_visible()


@pytest.mark.ui
def test_secure_page_after_login_fixture_module(ui_client_module):
    """
    Opens /login and logs in.
    Leaves the shared page on /secure for the next test.
    """
    login_page = LoginPage(ui_client_module.page)
    login_page.open()

    secure_page = login_page.login(
        "tomsmith",
        "SuperSecretPassword!",
    )

    assert login_page.is_login_success_message_visible(
        "You logged into a secure area!"
    )
    assert secure_page.get_url() == f"{ui_client_module.settings.ui_base_url}/secure"
    assert secure_page.is_logout_success_message_visible(
        "You logged into a secure area!"
    )


@pytest.mark.ui
def test_secure_page_logout_fixture_module(ui_client_module):
    """
    Intentionally no open() or login().
    Uses the same module-scoped page left on /secure
    by the previous test.
    Do not run this test alone.
    """
    secure_page = SecurePage(ui_client_module.page)

    assert secure_page.get_url() == f"{ui_client_module.settings.ui_base_url}/secure"

    login_page = secure_page.logout()

    assert secure_page.is_logout_success_message_visible(
        "You logged out of the secure area!"
    )
    assert login_page.is_login_success_message_visible(
        "You logged out of the secure area!"
    )
    assert login_page.get_url() == f"{ui_client_module.settings.ui_base_url}/login"
    assert login_page.is_username_visible()
    assert login_page.is_password_visible()