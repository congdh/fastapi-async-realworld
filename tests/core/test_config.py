import os

import pytest

from app.core.config import Settings

pytestmark = pytest.mark.asyncio


async def test_sqlalchemy_database_uri():
    expected = "postgresql://postgres@localhost"
    os.environ["SQLALCHEMY_DATABASE_URI"] = expected
    settings = Settings()
    settings.SQLALCHEMY_DATABASE_URI = expected
    assert isinstance(settings.SQLALCHEMY_DATABASE_URI, str)
    assert settings.SQLALCHEMY_DATABASE_URI == expected


@pytest.mark.parametrize(
    "testing,uri",
    [
        ("FALSE", "postgresql://postgres:postgres@localhost/example"),
        ("TRUE", "postgresql://postgres:postgres@localhost/test_example"),
    ],
)
async def test_postgres_config(testing: str, uri: str):
    if os.environ.get("SQLALCHEMY_DATABASE_URI"):
        os.environ.pop("SQLALCHEMY_DATABASE_URI")
    os.environ["POSTGRES_SERVER"] = "localhost"
    os.environ["POSTGRES_USER"] = "postgres"
    os.environ["POSTGRES_PASSWORD"] = "postgres"
    os.environ["POSTGRES_DB"] = "example"
    os.environ["TESTING"] = testing

    settings = Settings()
    assert isinstance(settings.SQLALCHEMY_DATABASE_URI, str)
    assert settings.SQLALCHEMY_DATABASE_URI == uri
