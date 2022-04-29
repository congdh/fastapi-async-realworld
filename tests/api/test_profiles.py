import pytest
from httpx import AsyncClient
from starlette import status

from app import schemas
from app.crud import crud_profile
from tests.utils.profile import assert_profile_with_user
from tests.utils.user import delete_user

pytestmark = pytest.mark.asyncio
API_PROFILES = "/api/profiles"
JWT_TOKEN_PREFIX = "Token"


async def test_get_profile_without_authorized(
    async_client: AsyncClient, test_user: schemas.UserDB
):
    r = await async_client.get(f"{API_PROFILES}/{test_user.username}")
    assert r.status_code == status.HTTP_200_OK
    profile_response = schemas.ProfileResponse(**r.json())
    profile = profile_response.profile
    assert_profile_with_user(profile, test_user)


async def test_get_profile_with_wrong_authorized(
    async_client: AsyncClient, test_user: schemas.UserDB, token: str
):
    wrong_signature_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MTA3NzM3LCJ1c2VybmFtZSI6InUxNTk2MzUyMDIxIiwiZXhwIjoxNjA0MjExMjUyfQ.qsyv6QGAIE1kk_ZQucj2IIs_zRvvO-HYqjMQ1Z9TGcw"  # noqa
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {wrong_signature_token}"}
    r = await async_client.get(f"{API_PROFILES}/{test_user.username}", headers=headers)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} failed_token"}
    r = await async_client.get(f"{API_PROFILES}/{test_user.username}", headers=headers)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    invalid_authorization = "invalid_authorization"
    headers = {"Authorization": invalid_authorization}
    r = await async_client.get(f"{API_PROFILES}/{test_user.username}", headers=headers)
    assert r.status_code == status.HTTP_200_OK

    headers = {"Authorization": f"{JWT_TOKEN_PREFIX}xxx failed_token"}
    r = await async_client.get(f"{API_PROFILES}/{test_user.username}", headers=headers)
    assert r.status_code == status.HTTP_200_OK
    profile_response = schemas.ProfileResponse(**r.json())
    profile = profile_response.profile
    assert_profile_with_user(profile, test_user)
    assert not profile.following

    await delete_user(test_user)
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    r = await async_client.get(f"{API_PROFILES}/{test_user.username}", headers=headers)
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    user_response = r.json()
    assert "detail" in user_response
    assert user_response["detail"] == "user not existed"


async def test_get_profile_with_authorized(
    async_client: AsyncClient, test_user: schemas.UserDB, token: str
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    r = await async_client.get(f"{API_PROFILES}/{test_user.username}", headers=headers)
    assert r.status_code == status.HTTP_200_OK
    profile_response = schemas.ProfileResponse(**r.json())
    profile = profile_response.profile
    assert_profile_with_user(profile, test_user)
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
    assert_profile_with_user(profile, other_user)
    assert profile.following


async def test_follow_without_authorized(
    async_client: AsyncClient, other_user: schemas.UserDB
):
    r = await async_client.post(f"{API_PROFILES}/{other_user.username}/follow")
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
    assert r.status_code == status.HTTP_400_BAD_REQUEST


async def test_follow_yourself(
    async_client: AsyncClient, test_user: schemas.UserDB, token: str
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    r = await async_client.post(
        f"{API_PROFILES}/{test_user.username}/follow", headers=headers
    )
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
    assert r.status_code == status.HTTP_200_OK
    profile_response = schemas.ProfileResponse(**r.json())
    profile = profile_response.profile
    assert_profile_with_user(profile, other_user)
    assert profile.following


async def test_unfollow_without_authorized(
    async_client: AsyncClient, other_user: schemas.UserDB
):
    r = await async_client.delete(f"{API_PROFILES}/{other_user.username}/follow")
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
    assert r.status_code == status.HTTP_400_BAD_REQUEST


async def test_unfollow_yourself(
    async_client: AsyncClient, test_user: schemas.UserDB, token: str
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    r = await async_client.delete(
        f"{API_PROFILES}/{test_user.username}/follow", headers=headers
    )
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
    assert r.status_code == status.HTTP_200_OK
    profile_response = schemas.ProfileResponse(**r.json())
    profile = profile_response.profile
    assert_profile_with_user(profile, other_user)
    assert not profile.following
