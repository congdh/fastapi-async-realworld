import pytest
from faker import Faker
from httpx import AsyncClient
from slugify import slugify

from app import schemas
from app.crud import crud_article, crud_profile
from tests.utils.article import create_test_article

pytestmark = pytest.mark.asyncio


async def test_create_article(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
) -> None:
    _article_in, article_id = await create_test_article(author=test_user)
    assert article_id


async def test_get_article_with_slug_not_existed(async_client: AsyncClient) -> None:
    slug = "not-existed-slug"
    assert not await crud_article.get_article_by_sluq(slug=slug)


async def test_get_article_with_id_not_existed(async_client: AsyncClient) -> None:
    article_id = 12345678
    assert not await crud_article.get(article_id=article_id)


async def test_get_article(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
) -> None:
    article_in, article_id = await create_test_article(author=test_user)
    slug = slugify(article_in.get("title"))
    article = await crud_article.get_article_by_sluq(slug=slug)
    assert article
    assert article.title == article_in.get("title")
    assert article.description == article_in.get("description")
    assert article.body == article_in.get("body")
    assert article.author_id == test_user.id
    assert article.slug == slug

    article = await crud_article.get(article_id=article_id)
    assert article
    assert article.title == article_in.get("title")
    assert article.description == article_in.get("description")
    assert article.body == article_in.get("body")
    assert article.author_id == test_user.id
    assert article.slug == slug


async def test_article_tags(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
) -> None:
    article_in, article_id = await create_test_article(author=test_user)
    faker = Faker()
    tag = faker.word()
    tags = [tag, faker.word()]
    await crud_article.add_article_tags(article_id=article_id, tags=tags)
    actual = await crud_article.get_article_tags(article_id=article_id)
    assert tag in actual
    await crud_article.remove_article_tags(article_id=article_id, tags=tags)
    actual = await crud_article.get_article_tags(article_id=article_id)
    assert tag not in actual


async def test_favorited_unfavorited(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    other_user: schemas.UserDB,
) -> None:
    article_in, article_id = await create_test_article(author=test_user)
    assert not await crud_article.is_article_favorited_by_user(
        article_id=article_id, user_id=other_user.id
    )
    assert await crud_article.count_article_favorites(article_id) == 0
    await crud_article.favorite(article_id=article_id, user_id=other_user.id)
    assert await crud_article.is_article_favorited_by_user(
        article_id=article_id, user_id=other_user.id
    )
    assert await crud_article.count_article_favorites(article_id) == 1
    await crud_article.unfavorite(article_id=article_id, user_id=other_user.id)
    assert not await crud_article.is_article_favorited_by_user(
        article_id=article_id, user_id=other_user.id
    )
    assert await crud_article.count_article_favorites(article_id) == 0


async def test_update_article(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
):
    article_in, article_id = await create_test_article(test_user)
    article_db = await crud_article.get(article_id)

    updated_body = "With two hands"
    faker = Faker()
    tags = [faker.word(), faker.word()]
    await crud_article.update(
        article_db=article_db,
        payload=schemas.ArticleInUpdate(body=updated_body, tagList=tags),
    )
    after_article_db = await crud_article.get(article_id)
    assert after_article_db.body == updated_body
    assert sorted(await crud_article.get_article_tags(article_id)) == sorted(tags)


@pytest.mark.parametrize(
    "tag_filter,author_filter,favorited_filter",
    [
        (False, False, False),
        (True, False, False),
        (False, True, False),
        (False, False, True),
    ],
)
async def test_get_all(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    other_user: schemas.UserDB,
    tag_filter: str,
    author_filter: str,
    favorited_filter: str,
):
    _article_in, article_id = await create_test_article(test_user)
    tag = None
    if tag_filter:
        tags = await crud_article.get_article_tags(article_id)
        if len(tags):
            tag = tags[0]
    author = test_user.username if author_filter else None
    favorited = None
    if favorited_filter:
        await crud_article.favorite(article_id=article_id, user_id=other_user.id)
        favorited = other_user.username
    article_dbs = await crud_article.get_all(
        tag=tag, author=author, favorited=favorited
    )
    assert len(article_dbs) > 0


async def test_feed(
    async_client: AsyncClient,
    test_user: schemas.UserDB,
    other_user: schemas.UserDB,
):
    article_in, _article_id = await create_test_article(other_user)
    slug = slugify(article_in.get("title"))
    await crud_profile.follow(other_user, test_user)

    articles = await crud_article.feed(follow_by=test_user.id)
    assert len(articles)
    article = articles[0]
    assert article.title == article_in.get("title")
    assert article.description == article_in.get("description")
    assert article.body == article_in.get("body")
    assert article.author_id == other_user.id
    assert article.slug == slug
