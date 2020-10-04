import datetime
from typing import Tuple

import pytest
from httpx import AsyncClient
from slugify import slugify
from starlette import status

from app import schemas
from app.crud import crud_article, crud_comment

pytestmark = pytest.mark.asyncio

API_ARTICLES = "/api/articles"
JWT_TOKEN_PREFIX = "Token"  # noqa: S105


async def create_test_article(author: schemas.UserDB) -> Tuple:
    article_in = {
        "title": "How to train your dragon" + datetime.datetime.now().__str__(),
        "description": "Ever wonder how?",
        "body": "You have to believe",
        "tagList": ["reactjs", "angularjs", "dragons"],
    }
    article_in_create = schemas.ArticleInCreate(**article_in)
    article_id = await crud_article.create(article_in_create, author.id)
    return article_in, article_id


async def test_add_comments_to_an_article(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
):
    article_in, article_id = await create_test_article(other_user)

    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    slug = slugify(article_in.get("title"))

    comment_in = {"body": "His name was my name too."}
    r = await async_client.post(
        f"{API_ARTICLES}/{slug}/comments", json={"comment": comment_in}, headers=headers
    )
    assert r.status_code == status.HTTP_200_OK
    comment_in_response = schemas.CommentInResponse(**r.json())
    comment = comment_in_response.comment
    assert comment.body == comment_in.get("body")
    assert comment.author.username == test_user.username


async def test_get_comments_from_an_article(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
):
    article_in, article_id = await create_test_article(other_user)

    comment_in = schemas.CommentInCreate(body="His name was my name too.")
    await crud_comment.create(
        payload=comment_in, article_id=article_id, author_id=test_user.id
    )
    await crud_comment.create(
        payload=comment_in, article_id=article_id, author_id=other_user.id
    )

    slug = slugify(article_in.get("title"))

    r = await async_client.get(f"{API_ARTICLES}/{slug}/comments")
    assert r.status_code == status.HTTP_200_OK
    multi_comments_in_response = schemas.MultipleCommentsInResponse(**r.json())
    assert len(multi_comments_in_response.comments) == 2
    comment = multi_comments_in_response.comments[0]
    assert comment.author.username == test_user.username
    assert comment.body == comment_in.body
    comment = multi_comments_in_response.comments[1]
    assert comment.author.username == other_user.username
    assert comment.body == comment_in.body


async def test_delete_comment_for_article(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
):
    article_in, article_id = await create_test_article(other_user)

    comment_in = schemas.CommentInCreate(body="His name was my name too.")
    comment_id = await crud_comment.create(
        payload=comment_in, article_id=article_id, author_id=test_user.id
    )

    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    slug = slugify(article_in.get("title"))
    r = await async_client.delete(
        f"{API_ARTICLES}/{slug}/comments/{comment_id}", headers=headers
    )
    assert r.status_code == status.HTTP_200_OK
    comment_db = await crud_comment.get(comment_id)
    assert comment_db is None
