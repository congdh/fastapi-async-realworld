from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status

from app import schemas
from app.core import security
from app.crud import users as crud_user

JWT_TOKEN_PREFIX = "Token"  # noqa: S105


def authrization_heder_token(
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


async def get_current_user(
    token: str = Depends(authrization_heder_token),
) -> schemas.UserDB:
    user_id = security.get_user_id_from_token(token=token)
    user_row = await crud_user.get(int(user_id))
    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserDB(**user_row)
