import datetime
from typing import Dict, Tuple

from app import schemas
from app.crud import crud_article

NOT_EXISTED_SLUG = "not-existed-article"
TEST_UPDATED_BODY = "With two hands"


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
    expected: Dict,
    actual: schemas.ArticleInResponse,
    author: schemas.UserDB,
    favorites_count=0,
    favorited=False,
    following=False,
) -> None:
    assert actual.title == expected.get("title")
    assert actual.description == expected.get("description")
    assert actual.body == expected.get("body")
    assert actual.author.username == author.username
    assert actual.author.following == following
    assert hasattr(actual, "tagList")
    assert actual.tagList == expected.get("tagList")
    assert hasattr(actual, "favorited")
    assert actual.favorited == favorited
    assert hasattr(actual, "favoritesCount")
    assert actual.favoritesCount == favorites_count
