import pytest
from httpx import AsyncClient
from slugify import slugify
from starlette import status

from app import schemas
from app.api.routers.articles import SLUG_NOT_FOUND
from app.crud import crud_article, crud_comment
from tests.utils.article import create_test_article
from tests.utils.comment import create_test_comment
from tests.utils.error import assert_error_response

pytestmark = pytest.mark.asyncio

API_ARTICLES = "/api/articles"
JWT_TOKEN_PREFIX = "Token"  # noqa: S105


async def test_add_comments_to_an_article_not_existed(
    async_client: AsyncClient,
    token: str,
):
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    slug = "not-existed-article"

    comment_in = {"body": "His name was my name too."}
    r = await async_client.post(
        f"{API_ARTICLES}/{slug}/comments", json={"comment": comment_in}, headers=headers
    )
    assert_error_response(r, status.HTTP_400_BAD_REQUEST, SLUG_NOT_FOUND)


async def test_add_comments_to_an_article(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
):
    article_in, _article_id = await create_test_article(other_user)

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


async def test_get_comments_from_an_article_not_existed(
    async_client: AsyncClient,
):
    slug = "not-existed-article"
    r = await async_client.get(f"{API_ARTICLES}/{slug}/comments")
    assert_error_response(
        r, status.HTTP_400_BAD_REQUEST, "article with this slug not found"
    )


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


async def test_delete_comment_for_article_not_existed(
    async_client: AsyncClient,
    token: str,
) -> None:
    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    slug = "not-existed-article"
    comment_id = 1
    r = await async_client.delete(
        f"{API_ARTICLES}/{slug}/comments/{comment_id}", headers=headers
    )
    assert_error_response(r, status.HTTP_400_BAD_REQUEST, SLUG_NOT_FOUND)


async def test_delete_comment_not_existed(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
) -> None:
    article_in, article_id = await create_test_article(other_user)

    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    slug = slugify(article_in.get("title"))
    comment_id = 999999
    r = await async_client.delete(
        f"{API_ARTICLES}/{slug}/comments/{comment_id}", headers=headers
    )
    assert_error_response(
        r, status.HTTP_400_BAD_REQUEST, "comment with this id not found"
    )


async def test_delete_comment_not_belong_to_article(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
) -> None:
    article_in, article_id = await create_test_article(other_user)
    article = await crud_article.get(article_id)
    comment_body, comment_id = await create_test_comment(
        article=article, author=test_user
    )

    article_in, article_id = await create_test_article(other_user)
    second_article = await crud_article.get(article_id)

    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    slug = slugify(second_article.title)
    r = await async_client.delete(
        f"{API_ARTICLES}/{slug}/comments/{comment_id}", headers=headers
    )
    assert_error_response(
        r, status.HTTP_400_BAD_REQUEST, "This comment is not belong to this article"
    )


async def test_delete_comment_not_belong_to_yourself(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
) -> None:
    article_in, article_id = await create_test_article(other_user)
    article = await crud_article.get(article_id)
    comment_body, comment_id = await create_test_comment(
        article=article, author=other_user
    )

    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    slug = article.slug
    r = await async_client.delete(
        f"{API_ARTICLES}/{slug}/comments/{comment_id}", headers=headers
    )
    assert_error_response(
        r,
        status.HTTP_403_FORBIDDEN,
        "You can not delete a comment is not belong to yourself",
    )


async def test_delete_comment_for_article(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    token: str,
    other_user: schemas.UserDB,
) -> None:
    article_in, article_id = await create_test_article(other_user)
    article = await crud_article.get(article_id)
    comment_body, comment_id = await create_test_comment(
        article=article, author=test_user
    )

    headers = {"Authorization": f"{JWT_TOKEN_PREFIX} {token}"}
    slug = slugify(article_in.get("title"))
    r = await async_client.delete(
        f"{API_ARTICLES}/{slug}/comments/{comment_id}", headers=headers
    )
    assert r.status_code == status.HTTP_200_OK
    comment_db = await crud_comment.get(comment_id)
    assert comment_db is None
