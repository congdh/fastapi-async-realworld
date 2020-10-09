from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app import schemas
from app.api import deps
from app.crud import crud_profile, crud_user

FOLLOW_SOMETHING_WRONG = "you cannot follow this user because something wrong"

router = APIRouter()


async def get_profile_response(
    username: str, requested_user: schemas.UserDB
) -> schemas.ProfileResponse:
    profile = await crud_profile.get_profile_by_username(
        username, requested_user=requested_user
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user not existed",
        )
    return schemas.ProfileResponse(profile=profile)


@router.get(
    "/{username}",
    name="Get a profile",
    description="Get a profile of a user of the system. Auth is optional",
    response_model=schemas.ProfileResponse,
)
async def get_profile(
    username: str,
    requested_user: schemas.UserDB = Depends(deps.get_current_user(required=False)),
) -> schemas.ProfileResponse:
    return await get_profile_response(requested_user=requested_user, username=username)


@router.post(
    "/{username}/follow",
    name="Follow a user",
    description="Follow a user by username",
    response_model=schemas.ProfileResponse,
)
async def follow_user(
    username: str,
    requested_user: schemas.UserDB = Depends(deps.get_current_user()),
) -> schemas.ProfileResponse:
    follower_user = await get_follow_user(
        requested_user=requested_user, username=username
    )
    if await crud_profile.is_following(follower_user, requested_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="you follow this user already",
        )
    await crud_profile.follow(follower_user, requested_user)
    return await get_profile_response(requested_user=requested_user, username=username)


async def get_follow_user(
    username: str, requested_user: schemas.UserDB
) -> schemas.UserDB:
    user_row = await crud_user.get_user_by_username(username=username)
    if user_row is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user with this username is not existed",
        )
    follower_user = schemas.UserDB(**user_row)
    if follower_user.id == requested_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cannot follow yourself",
        )
    return follower_user


@router.delete(
    "/{username}/follow",
    name="Unfollow a user",
    description="Unfollow a user by username",
    response_model=schemas.ProfileResponse,
)
async def unfollow_user(
    username: str,
    requested_user: schemas.UserDB = Depends(deps.get_current_user()),
) -> schemas.ProfileResponse:
    user_row = await crud_user.get_user_by_username(username=username)
    if user_row is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user with this username is not existed",
        )
    follower_user = schemas.UserDB(**user_row)
    if follower_user.id == requested_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cannot unfollow yourself",
        )
    if not await crud_profile.is_following(follower_user, requested_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="you don't follow this user already",
        )
    await crud_profile.unfollow(follower_user, requested_user)
    profile = await crud_profile.get_profile_by_username(username, requested_user)
    return schemas.ProfileResponse(profile=profile)  # type: ignore
