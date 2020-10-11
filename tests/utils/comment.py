from typing import Tuple

from app import schemas
from app.crud import crud_comment

TEST_COMMENT_BODY = "His name was my name too."


async def create_test_comment(
    article: schemas.ArticleDB, author: schemas.UserDB
) -> Tuple:
    comment_in = schemas.CommentInCreate(body=TEST_COMMENT_BODY)
    comment_id = await crud_comment.create(
        payload=comment_in, author_id=author.id, article_id=article.id
    )
    return TEST_COMMENT_BODY, comment_id
