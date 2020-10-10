from typing import Optional

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


async def get(user_id: int) -> Optional[schemas.UserDB]:
    query = db.users.select().where(user_id == db.users.c.id)
    user_row = await database.fetch_one(query=query)
    return schemas.UserDB(**user_row) if user_row else None


async def get_user_by_email(email: str) -> Optional[schemas.UserDB]:
    query = db.users.select().where(email == db.users.c.email)
    user_row = await database.fetch_one(query=query)
    return schemas.UserDB(**user_row) if user_row else None


async def get_user_by_username(username: str) -> Optional[schemas.UserDB]:
    query = db.users.select().where(username == db.users.c.username)
    user_row = await database.fetch_one(query=query)
    return schemas.UserDB(**user_row) if user_row else None


async def update(user_id: int, payload: schemas.UserUpdate) -> int:
    update_data = payload.dict(exclude_unset=True)
    query = (
        db.users.update()
        .where(user_id == db.users.c.id)
        .values(update_data)
        .returning(db.users.c.id)
    )
    return await database.execute(query=query)


async def authenticate(email: str, password: SecretStr) -> Optional[schemas.UserDB]:
    user_db = await get_user_by_email(email=email)
    if not user_db:
        return None
    if not verify_password(password, user_db.hashed_password):
        return None
    return user_db
