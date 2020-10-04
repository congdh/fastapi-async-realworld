from typing import Optional

from app import db, schemas
from app.crud import crud_user
from app.db import database


async def get_profile_by_username(
    username: str,
    requested_user: Optional[schemas.UserDB] = None,
) -> Optional[schemas.Profile]:
    user_row = await crud_user.get_user_by_username(username=username)
    if user_row is None:
        return None
    user = schemas.UserDB(**user_row)  # type: ignore
    profile = schemas.Profile(
        username=user.username, bio=user.bio, image=user.image  # type: ignore
    )
    profile.following = await is_following(user, requested_user)
    return profile


async def get_profile_by_user_id(
    user_id: int,
    requested_user: Optional[schemas.UserDB] = None,
) -> Optional[schemas.Profile]:
    user_row = await crud_user.get(user_id=user_id)
    if user_row is None:
        return None
    user = schemas.UserDB(**user_row)  # type: ignore
    profile = schemas.Profile(
        username=user.username, bio=user.bio, image=user.image  # type: ignore
    )
    profile.following = await is_following(user, requested_user)
    return profile


async def is_following(
    user: schemas.UserDB, requested_user: Optional[schemas.UserDB]
) -> bool:
    if requested_user is None:
        return False
    query = (
        db.followers_assoc.select()
        .where(user.id == db.followers_assoc.c.follower)
        .where(requested_user.id == db.followers_assoc.c.followed_by)
    )
    row = await database.fetch_one(query=query)
    return row is not None


async def follow(user: schemas.UserDB, requested_user: schemas.UserDB) -> bool:
    if await is_following(user=user, requested_user=requested_user):
        return False
    query = (
        db.followers_assoc.insert()
        .values(
            follower=user.id,
            followed_by=requested_user.id,
        )
        .returning(db.followers_assoc.c.follower)
    )
    row = await database.execute(query=query)
    return row is not None


async def unfollow(user: schemas.UserDB, requested_user: schemas.UserDB) -> bool:
    if not await is_following(user=user, requested_user=requested_user):
        return False
    query = (
        db.followers_assoc.delete()
        .where(db.followers_assoc.c.follower == user.id)
        .where(db.followers_assoc.c.followed_by == requested_user.id)
        .returning(db.followers_assoc.c.follower)
    )
    row = await database.execute(query=query)
    return row is not None
