import pytest
from faker import Faker
from httpx import AsyncClient

from app.crud import crud_tag

pytestmark = pytest.mark.asyncio


async def test_tag(
    async_client: AsyncClient,
):
    faker = Faker()
    tag = faker.word()
    assert not await crud_tag.create(tag)
    assert await crud_tag.is_existed_tag(tag)
    tags = await crud_tag.get_all_tags()
    assert tag in tags
