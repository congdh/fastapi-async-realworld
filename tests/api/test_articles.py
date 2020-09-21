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
        "article": {
            "title": "How to train your dragon",
            "description": "Ever wonder how?",
            "body": "You have to believe",
            "tagList": ["reactjs", "angularjs", "dragons"],
        }
    }
    r = await async_client.post(f"{API_ARTICLES}", json=article_in)
    assert r.status_code == status.HTTP_403_FORBIDDEN


async def test_create_articles(
    async_client: AsyncClient, test_user: schemas.UserDB, token: str
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    article_in = {
        "article": {
            "title": "How to train your dragon" + datetime.datetime.now().__str__(),
            "description": "Ever wonder how?",
            "body": "You have to believe",
            "tagList": ["reactjs", "angularjs", "dragons"],
        }
    }
    r = await async_client.post(f"{API_ARTICLES}", json=article_in, headers=headers)
    debug(r.json())
    assert r.status_code == status.HTTP_200_OK
    article = schemas.ArticleInResponse(**r.json()).article
    assert article.title == article_in.get("article").get("title")
    assert article.description == article_in.get("article").get("description")
    assert article.body == article_in.get("article").get("body")
    assert article.author.username == test_user.username
    assert hasattr(article, "tagList")
    assert article.tagList == article_in.get("article").get("tagList")
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
        "article": {
            "title": "How to train your dragon" + datetime.datetime.now().__str__(),
            "description": "Ever wonder how?",
            "body": "You have to believe",
            "tagList": ["reactjs", "angularjs", "dragons"],
        }
    }
    r = await async_client.post(f"{API_ARTICLES}", json=article_in, headers=headers)

    slug = slugify(article_in.get("article").get("title"))
    r = await async_client.get(f"{API_ARTICLES}/{slug}")
    debug(r.json())
    assert r.status_code == status.HTTP_200_OK
    article = schemas.ArticleInResponse(**r.json()).article
    assert article.title == article_in.get("article").get("title")
    assert article.description == article_in.get("article").get("description")
    assert article.body == article_in.get("article").get("body")
    assert article.author.username == test_user.username
    assert hasattr(article, "tagList")
    assert article.tagList == article_in.get("article").get("tagList")
    assert hasattr(article, "favorited")
    assert not article.favorited
    assert hasattr(article, "favoritesCount")
    assert article.favoritesCount == 0
