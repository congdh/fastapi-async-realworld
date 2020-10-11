import pytest
from httpx import AsyncClient

from app import schemas
from app.crud import crud_comment
from tests.utils.article import create_test_article
from tests.utils.comment import TEST_COMMENT_BODY

pytestmark = pytest.mark.asyncio


async def test_get_comment_not_existed(
    async_client: AsyncClient,
) -> None:
    comment_id = 999999
    assert not await crud_comment.get(comment_id)


async def test_create_and_get_comment(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    other_user: schemas.UserDB,
) -> None:
    _article_in, article_id = await create_test_article(author=test_user)
    assert article_id

    comment_id = await crud_comment.create(
        payload=schemas.CommentInCreate(body=TEST_COMMENT_BODY),
        author_id=other_user.id,
        article_id=article_id,
    )
    assert comment_id
    comment = await crud_comment.get(comment_id)
    assert comment.author_id == other_user.id
    assert comment.article_id == article_id
    assert comment.body == TEST_COMMENT_BODY


async def test_delete_comment(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    other_user: schemas.UserDB,
) -> None:
    article_in, article_id = await create_test_article(author=test_user)
    assert article_id

    comment_id = await crud_comment.create(
        payload=schemas.CommentInCreate(body=TEST_COMMENT_BODY),
        author_id=other_user.id,
        article_id=article_id,
    )
    assert comment_id
    await crud_comment.delete(comment_id)
    assert not await crud_comment.get(comment_id)


async def test_get_comments_from_an_article(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    other_user: schemas.UserDB,
) -> None:
    article_in, article_id = await create_test_article(author=test_user)
    assert article_id

    comment_id = await crud_comment.create(
        payload=schemas.CommentInCreate(body=TEST_COMMENT_BODY),
        author_id=other_user.id,
        article_id=article_id,
    )
    assert comment_id
    comments = await crud_comment.get_comments_from_an_article(article_id)
    assert len(comments) == 1
