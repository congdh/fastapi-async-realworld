import datetime

import pytest
from httpx import AsyncClient
from slugify import slugify
from starlette import status

from app import schemas
from app.api.routers.articles import SLUG_NOT_FOUND
from app.crud import crud_article, crud_profile
from tests.utils.article import assert_article_in_response, create_test_article
from tests.utils.error import assert_error_response

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


async def test_get_article_not_exited(async_client: AsyncClient):
    slug = "not-existed-slug"
    r = await async_client.get(f"{API_ARTICLES}/{slug}")
    assert r.status_code == status.HTTP_400_BAD_REQUEST


async def test_get_article(async_client: AsyncClient, test_user: schemas.UserDB):
    article_in, _article_id = await create_test_article(test_user)

    slug = slugify(article_in.get("title"))
    r = await async_client.get(f"{API_ARTICLES}/{slug}")
    assert r.status_code == status.HTTP_200_OK
    article = schemas.ArticleInResponse(**r.json()).article
    assert_article_in_response(article_in, article, test_user)


async def test_update_article_not_existed(
    async_client: AsyncClient, token: str
) -> None:
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    slug = "abcxyz"
    updated_data = {"body": "With two hands"}
    r = await async_client.put(
        f"{API_ARTICLES}/{slug}", json={"article": updated_data}, headers=headers
    )
    assert_error_response(r, status.HTTP_400_BAD_REQUEST, SLUG_NOT_FOUND)


async def test_update_article(
    async_client: AsyncClient, test_user: schemas.UserDB, token: str
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    article_in, _article_id = await create_test_article(test_user)
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


async def test_delete_article_not_existed(
    async_client: AsyncClient, token: str
) -> None:
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    slug = "abcxyz"
    r = await async_client.delete(f"{API_ARTICLES}/{slug}", headers=headers)
    assert_error_response(r, status.HTTP_400_BAD_REQUEST, SLUG_NOT_FOUND)


async def test_delete_article(
    async_client: AsyncClient, test_user: schemas.UserDB, token: str
) -> None:
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    article_in, _article_id = await create_test_article(test_user)
    slug = slugify(article_in.get("title"))

    r = await async_client.delete(f"{API_ARTICLES}/{slug}", headers=headers)
    assert r.status_code == status.HTTP_200_OK


async def test_delete_article_owner_by_other_user(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
) -> None:
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    article_in, _article_id = await create_test_article(other_user)
    slug = slugify(article_in.get("title"))

    r = await async_client.delete(f"{API_ARTICLES}/{slug}", headers=headers)
    assert_error_response(
        r,
        status_code=status.HTTP_403_FORBIDDEN,
        detail="can not delete an article owner by other user",
    )


@pytest.mark.parametrize(
    "tag_filter,author_filter,favorited_filter,authorization",
    [
        (False, False, False, False),
        (True, False, False, False),
        (False, True, False, False),
        (False, False, True, False),
        (False, False, False, True),
        (True, False, False, True),
        (False, True, False, True),
        (False, False, True, True),
    ],
)
async def test_list_articles(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
    tag_filter: bool,
    author_filter: bool,
    favorited_filter: bool,
    authorization: bool,
):
    article_in, article_id = await create_test_article(other_user)
    await crud_profile.follow(other_user, test_user)
    await crud_article.favorite(article_id=article_id, user_id=test_user.id)

    params = {}
    if tag_filter:
        tags = await crud_article.get_article_tags(article_id)
        if len(tags):
            tag = tags[0]
            params["tag"] = tag
    if author_filter:
        params["author"] = test_user.username
    if favorited_filter:
        params["favorited"] = other_user.username
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"} if authorization else {}
    r = await async_client.get(f"{API_ARTICLES}", params=params, headers=headers)
    assert r.status_code == status.HTTP_200_OK
    assert "articlesCount" in r.json()
    assert "articles" in r.json()
    assert r.json().get("articlesCount") == len(r.json().get("articles"))
    if len(r.json().get("articles")) > 0:
        article = schemas.ArticleForResponse(**r.json().get("articles")[0])
        assert_article_in_response(
            expected=article_in,
            actual=article,
            author=other_user,
            favorites_count=1,
            favorited=authorization,
            following=authorization,
        )


async def test_feed_articles(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    article_in, _article_id = await create_test_article(other_user)
    await crud_profile.follow(other_user, test_user)

    r = await async_client.get(f"{API_ARTICLES}/feed", headers=headers)
    assert r.status_code == status.HTTP_200_OK
    assert "articlesCount" in r.json()
    assert "articles" in r.json()
    assert r.json().get("articlesCount") == len(r.json().get("articles"))
    if len(r.json().get("articles")) > 0:
        article = schemas.ArticleForResponse(**r.json().get("articles")[0])
        assert_article_in_response(
            expected=article_in, actual=article, author=other_user, following=True
        )


async def test_favorite_unfavorited_article_not_existed(
    async_client: AsyncClient,
    token: str,
) -> None:
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    slug = "abcxyz"
    r = await async_client.post(f"{API_ARTICLES}/{slug}/favorite", headers=headers)
    assert_error_response(r, status.HTTP_400_BAD_REQUEST, SLUG_NOT_FOUND)
    r = await async_client.delete(f"{API_ARTICLES}/{slug}/favorite", headers=headers)
    assert_error_response(r, status.HTTP_400_BAD_REQUEST, SLUG_NOT_FOUND)


async def test_favorite_article(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
):
    article_in, _article_id = await create_test_article(other_user)

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
