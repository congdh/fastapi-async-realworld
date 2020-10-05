import datetime
from typing import Tuple

from app import schemas
from app.crud import crud_article


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
