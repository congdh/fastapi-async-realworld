from typing import Optional

from app import db, schemas
from app.crud import crud_user
from app.db import database


async def get_profile_by_username(
    username: str,
    requested_user: Optional[schemas.UserDB] = None,
) -> Optional[schemas.Profile]:
    user_db = await crud_user.get_user_by_username(username=username)
    if user_db is None:
        return None
    profile = schemas.Profile(
        username=user_db.username, bio=user_db.bio, image=user_db.image  # type: ignore
    )
    profile.following = await is_following(user_db, requested_user)
    return profile


async def get_profile_by_user_id(
    user_id: int,
    requested_user: Optional[schemas.UserDB] = None,
) -> Optional[schemas.Profile]:
    user_db = await crud_user.get(user_id=user_id)
    if user_db is None:
        return None
    profile = schemas.Profile(
        username=user_db.username, bio=user_db.bio, image=user_db.image  # type: ignore
    )
    profile.following = await is_following(user_db, requested_user)
    return profile


async def is_following(
    follower: schemas.UserDB, follower_by: Optional[schemas.UserDB]
) -> bool:
    if follower_by is None:
        return False
    query = (
        db.followers_assoc.select()
        .where(follower.id == db.followers_assoc.c.follower)
        .where(follower_by.id == db.followers_assoc.c.followed_by)
    )
    row = await database.fetch_one(query=query)
    return row is not None


async def follow(follower: schemas.UserDB, follower_by: schemas.UserDB) -> bool:
    if await is_following(follower=follower, follower_by=follower_by):
        return False
    query = (
        db.followers_assoc.insert()
        .values(
            follower=follower.id,
            followed_by=follower_by.id,
        )
        .returning(db.followers_assoc.c.follower)
    )
    row = await database.execute(query=query)
    return row is not None


async def unfollow(follower: schemas.UserDB, follower_by: schemas.UserDB) -> bool:
    if not await is_following(follower=follower, follower_by=follower_by):
        return False
    query = (
        db.followers_assoc.delete()
        .where(db.followers_assoc.c.follower == follower.id)
        .where(db.followers_assoc.c.followed_by == follower_by.id)
        .returning(db.followers_assoc.c.follower)
    )
    row = await database.execute(query=query)
    return row is not None
