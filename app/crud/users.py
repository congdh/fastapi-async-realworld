from typing import Any, Mapping, Optional

from pydantic import SecretStr

from app import db, schemas
from app.core.security import get_password_hash, verify_password
from app.db import database


async def create(payload: schemas.UserCreate) -> Optional[int]:
    query = db.users.insert().values(
        username=payload.username,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
    )
    return await database.execute(query=query)


async def get(id: int) -> Optional[Mapping[str, Any]]:
    query = db.users.select().where(id == db.users.c.id)
    return await database.fetch_one(query=query)


async def get_user_by_email(email: str) -> Optional[Mapping[str, Any]]:
    query = db.users.select().where(email == db.users.c.email)
    return await database.fetch_one(query=query)


async def authenticate(email: str, password: SecretStr) -> Optional[schemas.UserDB]:
    user_row = await get_user_by_email(email=email)
    if not user_row:
        return None
    user = schemas.UserDB(**user_row)
    if not verify_password(password, user.hashed_password):
        return None
    return user
