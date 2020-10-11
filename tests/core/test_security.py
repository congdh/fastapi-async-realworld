from datetime import timedelta

import pytest
from fastapi import HTTPException
from pydantic import SecretStr

from app.core.security import (
    create_access_token,
    get_password_hash,
    get_user_id_from_token,
    verify_password,
)

pytestmark = pytest.mark.asyncio


async def test_access_token():
    user_id = 1
    token = create_access_token(user_id)
    actual = get_user_id_from_token(token)
    assert int(actual) == user_id

    token = create_access_token(user_id, timedelta(minutes=1234))
    actual = get_user_id_from_token(token)
    assert int(actual) == user_id


def test_get_user_id_from_wrong_token():
    token = "wrong-token"
    with pytest.raises(HTTPException):
        get_user_id_from_token(token)


def test_verify_password():
    plain = "abcxyz"
    assert verify_password(
        plain_password=SecretStr(plain),
        hashed_password=get_password_hash(SecretStr(plain)),
    )


def test_verify_password_str():
    with pytest.raises(AttributeError, match=r"get_secret_value"):
        verify_password("abc", "abc")
