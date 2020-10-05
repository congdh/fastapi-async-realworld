import datetime
from typing import Dict

import pytest
from httpx import AsyncClient
from slugify import slugify
from starlette import status

from app import schemas
from app.crud import crud_article, crud_profile
from tests.utils.article import create_test_article

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
    assert r.status_code == status.HTTP_200_OK
    article = schemas.ArticleInResponse(**r.json()).article
    assert_article_in_response(article_in, article, test_user)


def assert_article_in_response(
    expected: Dict, actual: schemas.ArticleInResponse, author: schemas.UserDB
) -> None:
    assert actual.title == expected.get("title")
    assert actual.description == expected.get("description")
    assert actual.body == expected.get("body")
    assert actual.author.username == author.username
    assert hasattr(actual, "tagList")
    assert actual.tagList == expected.get("tagList")
    assert hasattr(actual, "favorited")
    assert not actual.favorited
    assert hasattr(actual, "favoritesCount")
    assert actual.favoritesCount == 0


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
    assert r.status_code == status.HTTP_200_OK
    article = schemas.ArticleInResponse(**r.json()).article
    assert_article_in_response(article_in, article, test_user)


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


@pytest.mark.parametrize(
    "tag,author,favorited",
    [
        (None, None, None),
        ("dragons", None, None),
        (None, "dragons", None),
    ],
)
async def test_list_articles_without_authentication(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
    tag: str,
    author: str,
    favorited: str,
):
    article_in = {
        "title": "How to train your dragon" + datetime.datetime.now().__str__(),
        "description": "Ever wonder how?",
        "body": "You have to believe",
        "tagList": ["reactjs", "angularjs", "dragons"],
    }
    article_in_create = schemas.ArticleInCreate(**article_in)
    await crud_article.create(article_in_create, other_user.id)
    await crud_profile.follow(other_user, test_user)

    params = {}
    if tag:
        params["tag"] = tag
    if author:
        params["author"] = test_user.username
    if favorited:
        params["favorited"] = favorited
    r = await async_client.get(f"{API_ARTICLES}", params=params)
    assert r.status_code == status.HTTP_200_OK
    assert "articlesCount" in r.json()
    assert "articles" in r.json()
    assert r.json().get("articlesCount") == len(r.json().get("articles"))
    if len(r.json().get("articles")) > 0:
        article = schemas.ArticleForResponse(**r.json().get("articles")[0])
        assert_article_in_response(article_in, article, other_user)
        assert (
            not article.author.following
        ), "List ariticles without authentication must be not following"


async def test_feed_articles(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    article_in = {
        "title": "How to train your dragon" + datetime.datetime.now().__str__(),
        "description": "Ever wonder how?",
        "body": "You have to believe",
        "tagList": ["reactjs", "angularjs", "dragons"],
    }
    article_in_create = schemas.ArticleInCreate(**article_in)
    await crud_article.create(article_in_create, other_user.id)
    await crud_profile.follow(other_user, test_user)

    r = await async_client.get(f"{API_ARTICLES}/feed", headers=headers)
    assert r.status_code == status.HTTP_200_OK
    assert "articlesCount" in r.json()
    assert "articles" in r.json()
    assert r.json().get("articlesCount") == len(r.json().get("articles"))
    if len(r.json().get("articles")) > 0:
        article = schemas.ArticleForResponse(**r.json().get("articles")[0])
        assert_article_in_response(article_in, article, other_user)
        assert article.author.following, "Feed ariticles must be following"


async def test_favorite_article(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
):
    article_in = {
        "title": "How to train your dragon" + datetime.datetime.now().__str__(),
        "description": "Ever wonder how?",
        "body": "You have to believe",
        "tagList": ["reactjs", "angularjs", "dragons"],
    }
    article_in_create = schemas.ArticleInCreate(**article_in)
    await crud_article.create(article_in_create, other_user.id)

    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    slug = slugify(article_in.get("title"))
    r = await async_client.post(f"{API_ARTICLES}/{slug}/favorite", headers=headers)
    assert r.status_code == status.HTTP_200_OK
    article = schemas.ArticleInResponse(**r.json()).article
    assert article.title == article_in.get("title")
    assert article.description == article_in.get("description")
    assert article.body == article_in.get("body")
    assert article.author.username == other_user.username
    assert hasattr(article, "tagList")
    assert article.tagList == article_in.get("tagList")
    assert hasattr(article, "favorited")
    assert article.favorited, "Favorited must be True"
    assert hasattr(article, "favoritesCount")
    assert article.favoritesCount > 0, "favoritesCount must great than 0"


async def test_unfavorite_article(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
):
    article_in, article_id = await create_test_article(other_user)
    await crud_article.favorite(article_id=article_id, user_id=test_user.id)

    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    slug = slugify(article_in.get("title"))
    r = await async_client.delete(f"{API_ARTICLES}/{slug}/favorite", headers=headers)
    assert r.status_code == status.HTTP_200_OK
    article = schemas.ArticleInResponse(**r.json()).article
    assert article.title == article_in.get("title")
    assert article.description == article_in.get("description")
    assert article.body == article_in.get("body")
    assert article.author.username == other_user.username
    assert hasattr(article, "tagList")
    assert article.tagList == article_in.get("tagList")
    assert hasattr(article, "favorited")
    assert not article.favorited, "Favorited must be False"
    assert hasattr(article, "favoritesCount")
