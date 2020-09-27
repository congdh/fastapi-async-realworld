import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

API_TAGS = "/api/tags"


async def test_list_all_tags(async_client: AsyncClient):
    r = await async_client.get(f"{API_TAGS}")
    assert r.status_code == status.HTTP_200_OK
    assert "tags" in r.json()
