from typing import List

from app import db
from app.db import database


async def get_all_tags() -> List[str]:
    query = db.tags.select()
    results = await database.fetch_all(query=query)
    return [tag.__getitem__("tag") for tag in results]


async def create(tag: str) -> str:
    query = db.tags.insert().values(tag=tag)
    return await database.execute(query=query)


async def is_existed_tag(tag: str) -> bool:
    query = db.tags.select().where(tag == db.tags.c.tag)
    tag_row = await database.fetch_one(query=query)
    return tag_row is not None
