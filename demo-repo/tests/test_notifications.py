# pyrefly: ignore [missing-import]
from src.notifications import get_user_email, is_valid_email


def test_is_valid_email():
    assert is_valid_email("user@example.com") is True
    assert is_valid_email("userexample.com") is False
    assert is_valid_email("user@example") is False


def test_get_user_email():
    assert get_user_email(None) == "unknown@example.com"
    assert get_user_email({"email": "foo@bar.com"}) == "foo@bar.com"
