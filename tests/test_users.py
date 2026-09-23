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