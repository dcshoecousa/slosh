from datetime import timedelta

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verify() -> None:
    password = "super-secret-password"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True
    assert verify_password("wrong-password", password_hash) is False


def test_create_and_decode_access_token() -> None:
    token = create_access_token("123", expires_delta=timedelta(minutes=5))
    payload = decode_access_token(token)

    assert payload["sub"] == "123"
    assert payload["type"] == "access"

