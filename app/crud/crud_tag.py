from typing import List

from app import db
from app.db import database


async def get_all_tags() -> List[str]:
    query = db.tags.select()
    results = await database.fetch_all(query=query)
    return [tag.__getitem__("tag") for tag in results]
