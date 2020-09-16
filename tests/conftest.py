from typing import AsyncGenerator

import pytest
from httpx import AsyncClient

from app import schemas
from app.core import security
from app.db import database
from app.main import app
from tests.utils.user import get_test_user


@pytest.fixture()
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await database.connect()
        yield ac
        await database.disconnect()


@pytest.fixture
async def test_user() -> schemas.UserDB:
    return await get_test_user()


@pytest.fixture
async def token(test_user: schemas.UserDB) -> str:
    return security.create_access_token(test_user.id)
