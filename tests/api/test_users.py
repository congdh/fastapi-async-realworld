from typing import Dict

import pytest
from faker import Faker
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio


async def test_read_users(async_client: AsyncClient):
    response = await async_client.get("/api/users")
    assert response.status_code == 200
    assert response.json() == [{"username": "Foo"}, {"username": "Bar"}]


API_USERS = "/api/users"
JWT_TOKEN_PREFIX = "Token"  # noqa: S105


async def test_register_success(async_client: AsyncClient):
    password = "password"
    faker = Faker()
    profile = faker.profile()
    email = profile.get("mail", None)
    username = profile.get("username", None)
    user_in = {"user": {"email": email, "password": password, "username": username}}
    r = await async_client.post(API_USERS, json=user_in)
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
    r = await async_client.post(API_USERS, json=user_in)
    assert r.status_code == status.HTTP_200_OK

    r = await async_client.post(API_USERS, json=user_in)
    user_response = r.json()
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in user_response
    assert (
        user_response["detail"]
        == "The user with this username already exists in the system."
    )
