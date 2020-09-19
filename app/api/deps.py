from typing import Callable, Optional

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status

from app import schemas
from app.core import security
from app.crud import crud_user

JWT_TOKEN_PREFIX = "Token"  # noqa: S105


def authrization_heder_token_required(
    api_key: str = Depends(APIKeyHeader(name="Authorization")),
) -> str:
    try:
        token_prefix, token = api_key.split(" ")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="unsupported authorization type",
        )
    if token_prefix != JWT_TOKEN_PREFIX:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="unsupported authorization type",
        )
    return token


def authrization_heder_token_optional(
    api_key: str = Depends(APIKeyHeader(name="Authorization", auto_error=False)),
) -> Optional[str]:
    if api_key is None:
        return None
    try:
        token_prefix, token = api_key.split(" ")
    except ValueError:
        return None
    if token_prefix != JWT_TOKEN_PREFIX:
        return None
    return token


def authrization_heder_token(required: bool = True) -> Callable:  # type: ignore
    return (
        authrization_heder_token_required
        if required
        else authrization_heder_token_optional
    )


async def get_current_user_required(
    token: str = Depends(authrization_heder_token()),
) -> schemas.UserDB:
    user_id = security.get_user_id_from_token(token=token)
    user_row = await crud_user.get(int(user_id))
    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserDB(**user_row)


async def get_current_user_required_optional(
    token: str = Depends(authrization_heder_token(required=False)),
) -> Optional[schemas.UserDB]:
    if token is None:
        return None
    user_id = security.get_user_id_from_token(token=token)
    user_row = await crud_user.get(int(user_id))
    if not user_row:
        return None
    return schemas.UserDB(**user_row)


def get_current_user(required: bool = True) -> Callable:  # type: ignore
    return get_current_user_required if required else get_current_user_required_optional
