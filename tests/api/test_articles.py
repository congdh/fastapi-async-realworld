import datetime

import pytest
from devtools import debug
from httpx import AsyncClient
from slugify import slugify
from starlette import status

from app import schemas

pytestmark = pytest.mark.asyncio

API_ARTICLES = "/api/articles"
JWT_TOKEN_PREFIX = "Token"  # noqa: S105


async def test_create_articles_without_authen(async_client: AsyncClient):
    article_in = {
        "title": "How to train your dragon",
        "description": "Ever wonder how?",
        "body": "You have to believe",
        "tagList": ["reactjs", "angularjs", "dragons"],
    }
    r = await async_client.post(f"{API_ARTICLES}", json={"article": article_in})
    assert r.status_code == status.HTTP_403_FORBIDDEN


async def test_create_articles(
    async_client: AsyncClient, test_user: schemas.UserDB, token: str
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    article_in = {
        "title": "How to train your dragon" + datetime.datetime.now().__str__(),
        "description": "Ever wonder how?",
        "body": "You have to believe",
        "tagList": ["reactjs", "angularjs", "dragons"],
    }
    r = await async_client.post(
        f"{API_ARTICLES}", json={"article": article_in}, headers=headers
    )
    debug(r.json())
    assert r.status_code == status.HTTP_200_OK
    article = schemas.ArticleInResponse(**r.json()).article
    assert article.title == article_in.get("title")
    assert article.description == article_in.get("description")
    assert article.body == article_in.get("body")
    assert article.author.username == test_user.username
    assert hasattr(article, "tagList")
    assert article.tagList == article_in.get("tagList")
    assert hasattr(article, "favorited")
    assert not article.favorited
    assert hasattr(article, "favoritesCount")
    assert article.favoritesCount == 0


async def test_get_article_not_exited(async_client: AsyncClient):
    slug = "not-existed-slug"
    r = await async_client.get(f"{API_ARTICLES}/{slug}")
    assert r.status_code == status.HTTP_400_BAD_REQUEST


async def test_get_article(
    async_client: AsyncClient, test_user: schemas.UserDB, token: str
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    article_in = {
        "title": "How to train your dragon" + datetime.datetime.now().__str__(),
        "description": "Ever wonder how?",
        "body": "You have to believe",
        "tagList": ["reactjs", "angularjs", "dragons"],
    }
    r = await async_client.post(
        f"{API_ARTICLES}", json={"article": article_in}, headers=headers
    )

    slug = slugify(article_in.get("title"))
    r = await async_client.get(f"{API_ARTICLES}/{slug}")
    debug(r.json())
    assert r.status_code == status.HTTP_200_OK
    article = schemas.ArticleInResponse(**r.json()).article
    assert article.title == article_in.get("title")
    assert article.description == article_in.get("description")
    assert article.body == article_in.get("body")
    assert article.author.username == test_user.username
    assert hasattr(article, "tagList")
    assert article.tagList == article_in.get("tagList")
    assert hasattr(article, "favorited")
    assert not article.favorited
    assert hasattr(article, "favoritesCount")
    assert article.favoritesCount == 0


async def test_update_article(
    async_client: AsyncClient, test_user: schemas.UserDB, token: str
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    article_in = {
        "title": "How to train your dragon" + datetime.datetime.now().__str__(),
        "description": "Ever wonder how?",
        "body": "You have to believe",
        "tagList": ["reactjs", "angularjs", "dragons"],
    }
    r = await async_client.post(
        f"{API_ARTICLES}", json={"article": article_in}, headers=headers
    )
    slug = slugify(article_in.get("title"))

    updated_data = {"body": "With two hands"}
    r = await async_client.put(
        f"{API_ARTICLES}/{slug}", json={"article": updated_data}, headers=headers
    )
    debug(r.json())
    assert r.status_code == status.HTTP_200_OK
    article = schemas.ArticleInResponse(**r.json()).article
    assert (
        article.title == updated_data.get("title")
        if "title" in updated_data
        else article_in.get("title")
    )
    assert (
        article.description == updated_data.get("description")
        if "description" in updated_data
        else article_in.get("description")
    )
    assert (
        article.body == updated_data.get("body")
        if "body" in updated_data
        else article_in.get("body")
    )
    assert article.author.username == test_user.username
    assert hasattr(article, "tagList")
    assert (
        article.tagList == updated_data.get("tagList")
        if "tagList" in updated_data
        else article_in.get("tagList")
    )
    assert hasattr(article, "favorited")
    assert not article.favorited
    assert hasattr(article, "favoritesCount")
    assert article.favoritesCount == 0


async def test_delete_article(
    async_client: AsyncClient, test_user: schemas.UserDB, token: str
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    article_in = {
        "title": "How to train your dragon" + datetime.datetime.now().__str__(),
        "description": "Ever wonder how?",
        "body": "You have to believe",
        "tagList": ["reactjs", "angularjs", "dragons"],
    }
    r = await async_client.post(
        f"{API_ARTICLES}", json={"article": article_in}, headers=headers
    )
    slug = slugify(article_in.get("title"))

    r = await async_client.delete(f"{API_ARTICLES}/{slug}", headers=headers)
    assert r.status_code == status.HTTP_200_OK
