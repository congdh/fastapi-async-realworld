from typing import Callable, Optional

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status

from app import schemas
from app.core import security
from app.crud import crud_user

JWT_PREFIX = "Token"


def authorization_heder_token_required(
    api_key: str = Depends(APIKeyHeader(name="Authorization")),
) -> str:
    try:
        token_prefix, token = api_key.split(" ")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="unsupported authorization type",
        )
    if token_prefix != JWT_PREFIX:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="unsupported authorization type",
        )
    return token


def authorization_heder_token_optional(
    api_key: str = Depends(APIKeyHeader(name="Authorization", auto_error=False)),
) -> Optional[str]:
    if api_key is None:
        return None
    try:
        token_prefix, token = api_key.split(" ")
    except ValueError:
        return None
    if token_prefix != JWT_PREFIX:
        return None
    return token


def authorization_heder_token(required: bool = True) -> Callable:  # type: ignore
    return (
        authorization_heder_token_required
        if required
        else authorization_heder_token_optional
    )


async def get_current_user_required(
    token: str = Depends(authorization_heder_token()),
) -> schemas.UserDB:
    user_id = security.get_user_id_from_token(token=token)
    user_db = await crud_user.get(int(user_id))
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    return user_db


async def get_current_user_required_optional(
    token: str = Depends(authorization_heder_token(required=False)),
) -> Optional[schemas.UserDB]:
    if token is None:
        return None
    user_id = security.get_user_id_from_token(token=token)
    return await crud_user.get(int(user_id))


def get_current_user(required: bool = True) -> Callable:  # type: ignore
    return get_current_user_required if required else get_current_user_required_optional
