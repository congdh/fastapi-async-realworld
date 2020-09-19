import pathlib
import sys
from os import environ
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy_utils import create_database, database_exists, drop_database

from alembic import command
from alembic.config import Config

environ["TESTING"] = "True"

from app import schemas  # noqa: E402
from app.core import security  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.db import database  # noqa: E402
from app.main import app  # noqa: E402
from tests.utils.user import get_test_user  # noqa: E402

sys.path.append(str(pathlib.Path().absolute().parent))

DROP_DATABASE_AFTER_TEST = False


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    root_dir = pathlib.Path(__file__).absolute().parent.parent
    ini_file = root_dir.joinpath("alembic.ini").__str__()
    alembic_directory = root_dir.joinpath("alembic").__str__()
    url = settings.SQLALCHEMY_DATABASE_URI
    if DROP_DATABASE_AFTER_TEST:
        assert not database_exists(url), "Test database already exists. Aborting tests."
    elif not database_exists(url):
        create_database(url)  # Create the test database.

    config = Config(ini_file)  # Run the migrations.
    config.set_main_option("script_location", alembic_directory)
    command.upgrade(config, "head")
    yield  # Run the tests.
    if DROP_DATABASE_AFTER_TEST:
        drop_database(url)  # Drop the test database.


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
async def other_user() -> schemas.UserDB:
    return await get_test_user()


@pytest.fixture
async def token(test_user: schemas.UserDB) -> str:
    return security.create_access_token(test_user.id)
