import pytest
from lab_fw.data.users import make_user


def test_make_user_defaults():
    user = make_user()
    assert user["email"] == "user@example.com"
    assert user["role"] == "user"
    assert user["active"] is True


def test_make_user_overrides():
    user = make_user(role="admin", active=False)
    assert user["role"] == "admin"
    assert user["active"] is False
    assert user["email"] == "user@example.com"

@pytest.mark.parametrize(
    ("role", "active"),
    [
        ("user", True),
        ("admin", True),
        ("guest", False),
    ],
    ids=["default-user", "admin-active", "guest-inactive"],
)

def test_make_user_roles(role, active):
    user = make_user(role=role, active=active)
    assert user["role"] == role
    assert user["active"] is active