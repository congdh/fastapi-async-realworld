import pytest
from devtools import debug
from faker import Faker
from httpx import AsyncClient
from pydantic import SecretStr

from app import schemas
from app.crud import crud_user
from tests.utils.user import TEST_USER_PASSWORD

pytestmark = pytest.mark.asyncio


async def test_create(async_client: AsyncClient) -> None:
    faker = Faker()
    profile = faker.profile()
    TEST_USER_EMAIL = profile.get("mail", None)
    TEST_USER_USERNAME = profile.get("username", None)
    user_in = schemas.UserCreate(
        email=TEST_USER_EMAIL,
        username=TEST_USER_USERNAME,
        password=TEST_USER_PASSWORD,
    )
    user_id = await crud_user.create(payload=user_in)
    debug(user_id)
    assert user_id
    user_db = await crud_user.get(user_id)
    debug(user_db)
    assert user_db
    assert user_db.email == user_in.email
    assert user_db.username == user_in.username


async def test_get_by_email(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
) -> None:
    actual = await crud_user.get_user_by_email(test_user.email)
    assert actual
    assert actual == test_user


async def test_get_by_username(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
) -> None:
    actual = await crud_user.get_user_by_username(test_user.username)
    assert actual
    assert actual == test_user


async def test_update(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
) -> None:
    new_username = test_user.username + "xxx"
    user_id = await crud_user.update(
        user_id=test_user.id, payload=schemas.UserUpdate(username=new_username)
    )
    actual = await crud_user.get(user_id)
    assert actual
    assert actual.id == test_user.id
    assert actual.email == test_user.email
    assert actual.username == new_username


async def test_authentication_with_not_existed_user(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
) -> None:
    actual = await crud_user.authenticate(
        test_user.email + "xxx", SecretStr(TEST_USER_PASSWORD)
    )
    assert not actual


async def test_authentication_wrong_password(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
) -> None:
    actual = await crud_user.authenticate(
        test_user.email, SecretStr(TEST_USER_PASSWORD + "xxx")
    )
    assert not actual


async def test_authentication_success(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
) -> None:
    actual = await crud_user.authenticate(
        test_user.email, SecretStr(TEST_USER_PASSWORD)
    )
    assert actual
    assert actual == test_user
