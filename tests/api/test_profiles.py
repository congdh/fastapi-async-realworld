import pytest
from devtools import debug
from httpx import AsyncClient
from starlette import status

from app import schemas

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
    assert profile.following
