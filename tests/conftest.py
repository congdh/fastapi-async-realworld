from typing import AsyncGenerator

import pytest
from httpx import AsyncClient

from app.db import database
from app.main import app


@pytest.fixture()
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await database.connect()
        yield ac
        await database.disconnect()
