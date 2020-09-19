import pytest
from devtools import debug
from httpx import AsyncClient
from starlette import status

from app import schemas
from app.crud import crud_profile

pytestmark = pytest.mark.asyncio
API_PROFILES = "/api/profiles"
JWT_TOKEN_PREFIX = "Token"  # noqa: S105


async def test_get_profile_without_authorized(
    async_client: AsyncClient, test_user: schemas.UserDB
):
    r = await async_client.get(f"{API_PROFILES}/{test_user.username}")
    debug(r.json())
    assert r.status_code == status.HTTP_200_OK
    profile_response = schemas.ProfileResponse(**r.json())
    profile = profile_response.profile
    assert profile.username == test_user.username
    assert profile.bio == test_user.bio
    assert profile.image == test_user.image


async def test_get_profile_with_authorized(
    async_client: AsyncClient, test_user: schemas.UserDB, token: str
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    r = await async_client.get(f"{API_PROFILES}/{test_user.username}", headers=headers)
    debug(r.json())
    assert r.status_code == status.HTTP_200_OK
    profile_response = schemas.ProfileResponse(**r.json())
    profile = profile_response.profile
    assert profile.username == test_user.username
    assert profile.bio == test_user.bio
    assert profile.image == test_user.image
    assert not profile.following


async def test_get_profile_with_following(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
):
    result = await crud_profile.follow(other_user, test_user)
    assert result
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    r = await async_client.get(f"{API_PROFILES}/{other_user.username}", headers=headers)
    assert r.status_code == status.HTTP_200_OK
    profile_response = schemas.ProfileResponse(**r.json())
    profile = profile_response.profile
    assert profile.username == other_user.username
    assert profile.bio == other_user.bio
    assert profile.image == other_user.image
    assert profile.following


async def test_follow_without_authorized(
    async_client: AsyncClient, other_user: schemas.UserDB
):
    r = await async_client.post(f"{API_PROFILES}/{other_user.username}/follow")
    debug(r.json())
    assert r.status_code == status.HTTP_403_FORBIDDEN


async def test_follow_not_existed_user(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    r = await async_client.post(
        f"{API_PROFILES}/{other_user.username}xxx/follow", headers=headers
    )
    debug(r.json())
    assert r.status_code == status.HTTP_400_BAD_REQUEST


async def test_follow_yourself(
    async_client: AsyncClient, test_user: schemas.UserDB, token: str
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    r = await async_client.post(
        f"{API_PROFILES}/{test_user.username}/follow", headers=headers
    )
    debug(r.json())
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json().get("detail"), "cannot follow yourself"


async def test_follow_user_who_follow_already(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
):
    result = await crud_profile.follow(other_user, test_user)
    assert result
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    r = await async_client.post(
        f"{API_PROFILES}/{other_user.username}/follow", headers=headers
    )
    debug(r.json())
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json().get("detail"), "you follow this user already"


async def test_follow_user(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    r = await async_client.post(
        f"{API_PROFILES}/{other_user.username}/follow", headers=headers
    )
    debug(r.json())
    assert r.status_code == status.HTTP_200_OK
    profile_response = schemas.ProfileResponse(**r.json())
    profile = profile_response.profile
    assert profile.username == other_user.username
    assert profile.bio == other_user.bio
    assert profile.image == other_user.image
    assert profile.following


async def test_unfollow_without_authorized(
    async_client: AsyncClient, other_user: schemas.UserDB
):
    r = await async_client.delete(f"{API_PROFILES}/{other_user.username}/follow")
    debug(r.json())
    assert r.status_code == status.HTTP_403_FORBIDDEN


async def test_unfollow_not_existed_user(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    r = await async_client.delete(
        f"{API_PROFILES}/{other_user.username}xxx/follow", headers=headers
    )
    debug(r.json())
    assert r.status_code == status.HTTP_400_BAD_REQUEST


async def test_unfollow_yourself(
    async_client: AsyncClient, test_user: schemas.UserDB, token: str
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    r = await async_client.delete(
        f"{API_PROFILES}/{test_user.username}/follow", headers=headers
    )
    debug(r.json())
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json().get("detail"), "cannot follow yourself"


async def test_unfollow_user_you_dont_follow_already(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    r = await async_client.delete(
        f"{API_PROFILES}/{other_user.username}/follow", headers=headers
    )
    debug(r.json())
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json().get("detail"), "you don't follow this user already"


async def test_unfollow_user(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
):
    result = await crud_profile.follow(other_user, test_user)
    assert result
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    r = await async_client.delete(
        f"{API_PROFILES}/{other_user.username}/follow", headers=headers
    )
    debug(r.json())
    assert r.status_code == status.HTTP_200_OK
    profile_response = schemas.ProfileResponse(**r.json())
    profile = profile_response.profile
    assert profile.username == other_user.username
    assert profile.bio == other_user.bio
    assert profile.image == other_user.image
    assert not profile.following
