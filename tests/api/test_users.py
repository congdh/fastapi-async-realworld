import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_read_users(async_client: AsyncClient):
    response = await async_client.get("/api/users")
    assert response.status_code == 200
    assert response.json() == [{'username': 'Foo'}, {'username': 'Bar'}]
