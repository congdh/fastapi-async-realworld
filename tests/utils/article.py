import datetime
from typing import Dict, Tuple

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


def assert_article_in_response(
    expected: Dict, actual: schemas.ArticleInResponse, author: schemas.UserDB
) -> None:
    assert actual.title == expected.get("title")
    assert actual.description == expected.get("description")
    assert actual.body == expected.get("body")
    assert actual.author.username == author.username
    assert hasattr(actual, "tagList")
    assert actual.tagList == expected.get("tagList")
    assert hasattr(actual, "favorited")
    assert not actual.favorited
    assert hasattr(actual, "favoritesCount")
    assert actual.favoritesCount == 0
