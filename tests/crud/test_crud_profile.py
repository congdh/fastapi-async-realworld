import pytest
from httpx import AsyncClient

from app import schemas
from app.crud import crud_profile
from tests.utils.profile import assert_profile_with_user

pytestmark = pytest.mark.asyncio


async def test_get_profile_by_username_not_existed(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    other_user: schemas.UserDB,
) -> None:
    profile = await crud_profile.get_profile_by_username(
        username=test_user.username + "xxx"
    )
    assert not profile


async def test_get_profile_by_username(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    other_user: schemas.UserDB,
) -> None:
    profile = await crud_profile.get_profile_by_username(username=test_user.username)
    assert_profile_with_user(profile, test_user)


async def test_get_profile_by_user_id_not_existed(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    other_user: schemas.UserDB,
) -> None:
    profile = await crud_profile.get_profile_by_user_id(user_id=test_user.id + 100000)
    assert not profile


async def test_get_profile_by_user_id(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    other_user: schemas.UserDB,
) -> None:
    profile = await crud_profile.get_profile_by_user_id(user_id=test_user.id)
    assert_profile_with_user(profile, test_user)


async def test_follow_unfollow(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    other_user: schemas.UserDB,
) -> None:
    assert not await crud_profile.is_following(
        follower=other_user, follower_by=test_user
    )
    assert not await crud_profile.unfollow(follower=other_user, follower_by=test_user)
    assert await crud_profile.follow(follower=other_user, follower_by=test_user)
    assert await crud_profile.is_following(follower=other_user, follower_by=test_user)
    assert not await crud_profile.follow(follower=other_user, follower_by=test_user)
    assert await crud_profile.unfollow(follower=other_user, follower_by=test_user)
