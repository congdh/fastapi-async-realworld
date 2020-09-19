import pytest
from httpx import AsyncClient
from starlette import status

from app.schemas import ProfileResponse, UserDB

pytestmark = pytest.mark.asyncio
API_PROFILES = "/api/profiles"


async def test_get_profile(async_client: AsyncClient, test_user: UserDB):
    r = await async_client.get(f"{API_PROFILES}/{test_user.username}")
    assert r.status_code == status.HTTP_200_OK
    profile_response = ProfileResponse(**r.json())
    profile = profile_response.profile
    assert profile.username == test_user.username
    assert profile.bio == test_user.bio
    assert profile.image == test_user.image
