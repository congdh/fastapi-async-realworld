from typing import Dict

import pytest
from faker import Faker
from httpx import AsyncClient
from starlette import status

from app import schemas
from tests.utils.user import TEST_USER_PASSWORD

pytestmark = pytest.mark.asyncio

API_AUTHENTICATION = "/api/users"
API_USERS = "/api/user"
JWT_TOKEN_PREFIX = "Token"  # noqa: S105


async def test_register_success(async_client: AsyncClient):
    password = "password"
    faker = Faker()
    profile = faker.profile()
    email = profile.get("mail", None)
    username = profile.get("username", None)
    user_in = {"user": {"email": email, "password": password, "username": username}}
    r = await async_client.post(API_AUTHENTICATION, json=user_in)
    user_response = r.json()
    assert r.status_code == status.HTTP_200_OK
    assert "user" in user_response
    user_with_token = user_response.get("user")
    assert isinstance(user_with_token, Dict)
    assert "email" in user_with_token
    assert user_with_token["email"] == email
    assert "username" in user_with_token
    assert user_with_token["username"] == username
    assert "token" in user_with_token
    assert "bio" in user_with_token


async def test_register_failure_by_existed_user(async_client: AsyncClient):
    password = "password"
    faker = Faker()
    profile = faker.profile()
    email = profile.get("mail", None)
    username = profile.get("username", None)
    user_in = {"user": {"email": email, "password": password, "username": username}}
    r = await async_client.post(API_AUTHENTICATION, json=user_in)
    assert r.status_code == status.HTTP_200_OK

    r = await async_client.post(API_AUTHENTICATION, json=user_in)
    user_response = r.json()
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in user_response
    assert (
        user_response["detail"]
        == "The user with this username already exists in the system."
    )


async def test_user_login_failure(async_client: AsyncClient):
    login_data = {"user": {"email": "u1596352021xxx", "password": "passwordxxx"}}
    r = await async_client.post("/api/users/login", json=login_data)
    user_response = r.json()
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in user_response
    assert user_response["detail"] == "Incorrect email or password"


async def test_user_login_failure_incorrect_password(
    async_client: AsyncClient, test_user
):
    login_data = {
        "user": {"email": test_user.email, "password": TEST_USER_PASSWORD + "xxx"}
    }
    r = await async_client.post(f"{API_AUTHENTICATION}/login", json=login_data)
    user_response = r.json()
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in user_response
    assert user_response["detail"] == "Incorrect email or password"


async def test_user_login_success(async_client: AsyncClient, test_user):
    login_data = {"user": {"email": test_user.email, "password": TEST_USER_PASSWORD}}
    r = await async_client.post(f"{API_AUTHENTICATION}/login", json=login_data)
    assert r.status_code == status.HTTP_200_OK
    user_response = r.json()
    assert r.status_code == status.HTTP_200_OK
    assert "user" in user_response
    user_with_token = user_response.get("user")
    assert isinstance(user_with_token, Dict)
    assert "email" in user_with_token
    assert user_with_token["email"] == test_user.email
    assert "username" in user_with_token
    assert user_with_token["username"] == test_user.username
    assert "token" in user_with_token
    assert "bio" in user_with_token
    assert "image" in user_with_token


async def test_retrieve_current_user_without_token(async_client: AsyncClient):
    r = await async_client.get(API_USERS)
    assert r.status_code == status.HTTP_403_FORBIDDEN


async def test_retrieve_current_user_wrong_token(async_client: AsyncClient):
    invalid_authorization = "invalid_authorization"
    headers = {"Authorization": invalid_authorization}
    r = await async_client.get(API_USERS, headers=headers)
    assert r.status_code == status.HTTP_403_FORBIDDEN

    headers = {"Authorization": f"{JWT_TOKEN_PREFIX}xxx failed_token"}
    r = await async_client.get(API_USERS, headers=headers)
    assert r.status_code == status.HTTP_403_FORBIDDEN

    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} failed_token"}
    r = await async_client.get(API_USERS, headers=headers)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    wrong_signature_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MTA3NzM3LCJ1c2VybmFtZSI6InUxNTk2MzUyMDIxIiwiZXhwIjoxNjA0MjExMjUyfQ.qsyv6QGAIE1kk_ZQucj2IIs_zRvvO-HYqjMQ1Z9TGcw"  # noqa
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {wrong_signature_token}"}
    r = await async_client.get(API_USERS, headers=headers)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


async def test_retrieve_current_success(
    async_client: AsyncClient, test_user: schemas.UserDB, token: str
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    r = await async_client.get(API_USERS, headers=headers)
    assert r.status_code == status.HTTP_200_OK
    user_response = r.json()
    assert r.status_code == status.HTTP_200_OK
    assert "user" in user_response
    user_with_token = user_response.get("user")
    assert isinstance(user_with_token, Dict)
    assert "email" in user_with_token
    assert user_with_token["email"] == test_user.email
    assert "username" in user_with_token
    assert user_with_token["username"] == test_user.username
    assert "token" in user_with_token
    assert "bio" in user_with_token
    assert "image" in user_with_token


async def test_update_current_user_with_new_username(
    async_client: AsyncClient, test_user: schemas.UserDB, token: str
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    new_username = f"{test_user.username}xxx"
    user_update = {"user": {"username": new_username}}
    r = await async_client.put(API_USERS, json=user_update, headers=headers)
    assert r.status_code == status.HTTP_200_OK


async def test_update_current_user_with_new_email(
    async_client: AsyncClient, test_user: schemas.UserDB, token: str
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    new_email = f"{test_user.email}xxx"
    user_update = {"user": {"email": new_email}}
    r = await async_client.put(API_USERS, json=user_update, headers=headers)
    assert r.status_code == status.HTTP_200_OK
    user_response = r.json()
    assert r.status_code == status.HTTP_200_OK
    assert "user" in user_response
    user_with_token = user_response.get("user")
    assert isinstance(user_with_token, Dict)
    assert "email" in user_with_token
    assert user_with_token["email"] == new_email
    assert "username" in user_with_token
    assert user_with_token["username"] == test_user.username
    assert "token" in user_with_token
    assert "bio" in user_with_token
    assert "image" in user_with_token
