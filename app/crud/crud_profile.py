from typing import Optional

from app import schemas
from app.crud import users as crud_user


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
    if requested_user:
        profile.following = True
    return profile
