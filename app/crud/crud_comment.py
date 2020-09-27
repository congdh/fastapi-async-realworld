from typing import List, Optional

from app import db, schemas
from app.db import database


async def create(
    payload: schemas.CommentInCreate, article_id: int, author_id: int
) -> int:
    query = db.comments.insert().values(
        body=payload.body,
        author_id=author_id,
        article_id=article_id,
    )
    comment_id = await database.execute(query=query)
    return comment_id


async def get(id: int) -> Optional[schemas.CommentDB]:
    query = db.comments.select().where(id == db.comments.c.id)
    comment_row = await database.fetch_one(query=query)
    if comment_row:
        return schemas.CommentDB(**comment_row)
    else:
        return None


async def get_comments_from_an_article(article_id: int) -> List[schemas.CommentDB]:
    query = db.comments.select().where(article_id == db.comments.c.article_id)
    comment_rows = await database.fetch_all(query=query)
    return [schemas.CommentDB(**row) for row in comment_rows]


async def delete(comment_id: int) -> None:
    query = db.comments.delete().where(comment_id == db.comments.c.id)
    await database.execute(query=query)
