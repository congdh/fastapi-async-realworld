from typing import List, Optional

from slugify import slugify
from sqlalchemy import func, select

from app import db, schemas
from app.crud import crud_tag
from app.db import database


async def add_article_tags(article_id: int, tags: List[str]) -> None:
    if len(tags) > 0:
        values = [{"article_id": article_id, "tag": tag} for tag in tags]
        query = db.tag_assoc.insert().values(values)
        await database.execute(query=query)


async def get_article_tags(article_id: int) -> List[str]:
    query = (
        db.tag_assoc.select()
        .with_only_columns([db.tag_assoc.c.tag])
        .where(article_id == db.tag_assoc.c.article_id)
    )
    tags = await database.fetch_all(query=query)
    return [tag.get("tag") for tag in tags]


async def create(payload: schemas.ArticleInCreate, current_user: schemas.UserDB) -> int:
    slug = slugify(payload.title)
    query = db.articles.insert().values(
        title=payload.title,
        description=payload.description,
        body=payload.body,
        slug=slug,
        author_id=current_user.id,
    )
    article_id = await database.execute(query=query)
    if payload.tagList:
        for tag in payload.tagList:
            if not await crud_tag.is_existed_tag(tag):
                await crud_tag.create(tag)
        await add_article_tags(article_id, payload.tagList)
    return article_id


async def get(id: int) -> Optional[schemas.ArticleDB]:
    query = db.articles.select().where(id == db.articles.c.id)
    article_row = await database.fetch_one(query=query)
    if article_row:
        return schemas.ArticleDB(**article_row)
    else:
        return None


async def get_article_by_sluq(slug: str) -> Optional[schemas.ArticleDB]:
    query = db.articles.select().where(slug == db.articles.c.slug)
    article_row = await database.fetch_one(query=query)
    if article_row:
        return schemas.ArticleDB(**article_row)
    else:
        return None


async def is_article_favorited_by_user(article_id: int, user_id: int) -> bool:
    query = (
        db.favoriter_assoc.select()
        .where(article_id == db.favoriter_assoc.c.article_id)
        .where(user_id == db.favoriter_assoc.c.user_id)
    )
    row = await database.fetch_one(query=query)
    return row is not None


async def count_article_favorites(article_id: int) -> int:
    query = (
        select([func.count()])
        .select_from(db.favoriter_assoc)
        .where(db.favoriter_assoc.c.article_id == article_id)
    )
    row = await database.fetch_one(query=query)
    return dict(**row).get("count_1", 0)
