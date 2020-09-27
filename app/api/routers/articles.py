from fastapi import APIRouter, Body, Depends, HTTPException
from starlette import status

from app import schemas
from app.api import deps
from app.crud import crud_article, crud_profile

router = APIRouter()


@router.post(
    "",
    name="Create an article",
    description="Create an article. Auth is required",
    response_model=schemas.ArticleInResponse,
)
async def create_article(
    article_in: schemas.ArticleInCreate = Body(..., embed=True, alias="article"),
    current_user: schemas.UserDB = Depends(deps.get_current_user()),
) -> schemas.ArticleInResponse:
    article_id = await crud_article.create(article_in, author_id=current_user.id)
    article = await crud_article.get(article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="you cannot create this article because something wrong",
        )
    profile = await crud_profile.get_profile_by_user_id(
        article.author_id, requested_user=current_user
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user not existed",
        )
    tags = await crud_article.get_article_tags(article_id)
    favorited = await crud_article.is_article_favorited_by_user(
        article_id, current_user.id
    )
    favorites_count = await crud_article.count_article_favorites(article_id)
    return schemas.ArticleInResponse(
        article=schemas.ArticleForResponse(
            slug=article.slug,
            title=article.title,
            description=article.description,
            body=article.body,
            createdAt=article.created_at,
            updatedAt=article.updated_at,
            author=profile,
            tagList=tags,
            favorited=favorited,
            favoritesCount=favorites_count,
        )
    )


@router.get(
    "/feed",
    name="Get recent articles from users you follow",
    description="Get most recent articles from users you follow. "
    "Use query parameters to limit. Auth is required",
    response_model=schemas.MultipleArticlesInResponse,
)
async def feed_articles(
    current_user: schemas.UserDB = Depends(deps.get_current_user()),
    limit: int = 20,
    offset: int = 0,
) -> schemas.MultipleArticlesInResponse:
    article_rows = await crud_article.feed(
        limit=limit, offset=offset, follow_by=current_user.id
    )
    articles = []
    for article_row in article_rows:
        article_db = schemas.ArticleDB(**article_row)  # type: ignore
        profile = await crud_profile.get_profile_by_user_id(
            article_db.author_id, requested_user=current_user
        )
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user not existed",
            )
        tags = await crud_article.get_article_tags(article_db.id)
        if current_user:
            favorited = await crud_article.is_article_favorited_by_user(
                article_db.id, current_user.id
            )
        else:
            favorited = False
        favorites_count = await crud_article.count_article_favorites(article_db.id)
        article_for_reponse = schemas.ArticleForResponse(
            slug=article_db.slug,
            title=article_db.title,
            description=article_db.description,
            body=article_db.body,
            createdAt=article_db.created_at,
            updatedAt=article_db.updated_at,
            author=profile,
            tagList=tags,
            favorited=favorited,
            favoritesCount=favorites_count,
        )
        articles.append(article_for_reponse)

    return schemas.MultipleArticlesInResponse(
        articles=articles, articlesCount=len(articles)
    )


@router.get(
    "/{slug}",
    name="Get an article",
    description="Get an article. Auth not required",
    response_model=schemas.ArticleInResponse,
)
async def get_article(
    slug: str,
    current_user: schemas.UserDB = Depends(deps.get_current_user(required=False)),
) -> schemas.ArticleInResponse:
    article = await crud_article.get_article_by_sluq(slug=slug)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="article with this slug not found",
        )
    profile = await crud_profile.get_profile_by_user_id(
        article.author_id, requested_user=current_user
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user not existed",
        )
    tags = await crud_article.get_article_tags(article.id)
    if current_user:
        favorited = await crud_article.is_article_favorited_by_user(
            article.id, current_user.id
        )
    else:
        favorited = False
    favorites_count = await crud_article.count_article_favorites(article.id)
    return schemas.ArticleInResponse(
        article=schemas.ArticleForResponse(
            slug=article.slug,
            title=article.title,
            description=article.description,
            body=article.body,
            createdAt=article.created_at,
            updatedAt=article.updated_at,
            author=profile,
            tagList=tags,
            favorited=favorited,
            favoritesCount=favorites_count,
        )
    )


@router.put(
    "/{slug}",
    name="Update an article",
    description="Update an article. Auth is required",
    response_model=schemas.ArticleInResponse,
)
async def update_article(
    slug: str,
    article_in: schemas.ArticleInUpdate = Body(..., embed=True, alias="article"),
    current_user: schemas.UserDB = Depends(deps.get_current_user()),
) -> schemas.ArticleInResponse:
    article_db = await crud_article.get_article_by_sluq(slug)
    if article_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="article with this slug not found",
        )
    await crud_article.update(article_db, payload=article_in)

    article = await crud_article.get_article_by_sluq(slug=slug)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="article with this slug not found",
        )
    profile = await crud_profile.get_profile_by_user_id(
        article.author_id, requested_user=current_user
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user not existed",
        )
    tags = await crud_article.get_article_tags(article.id)
    if current_user:
        favorited = await crud_article.is_article_favorited_by_user(
            article.id, current_user.id
        )
    else:
        favorited = False
    favorites_count = await crud_article.count_article_favorites(article.id)
    return schemas.ArticleInResponse(
        article=schemas.ArticleForResponse(
            slug=article.slug,
            title=article.title,
            description=article.description,
            body=article.body,
            createdAt=article.created_at,
            updatedAt=article.updated_at,
            author=profile,
            tagList=tags,
            favorited=favorited,
            favoritesCount=favorites_count,
        )
    )


@router.delete(
    "/{slug}",
    name="Delete an article",
    description="Delete an article. Auth is required",
)
async def delete_article(
    slug: str,
    current_user: schemas.UserDB = Depends(deps.get_current_user(required=False)),
) -> None:
    article_db = await crud_article.get_article_by_sluq(slug=slug)
    if article_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="article with this slug not found",
        )
    if article_db.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="can not delete an article owner by other user",
        )
    await crud_article.delete(article_db)


@router.get(
    "",
    name="Get recent articles globally",
    description="Get most recent articles globally. "
    "Use query parameters to filter results. Auth is optional",
    response_model=schemas.MultipleArticlesInResponse,
)
async def list_articles(
    current_user: schemas.UserDB = Depends(deps.get_current_user(required=False)),
    limit: int = 20,
    offset: int = 0,
    tag: str = None,
    author: str = None,
    favorited: str = None,
) -> schemas.MultipleArticlesInResponse:
    article_rows = await crud_article.get_all(
        limit=limit, offset=offset, tag=tag, author=author, favorited=favorited
    )
    articles = []
    for article_row in article_rows:
        article_db = schemas.ArticleDB(**article_row)  # type: ignore
        profile = await crud_profile.get_profile_by_user_id(
            article_db.author_id, requested_user=current_user
        )
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user not existed",
            )
        tags = await crud_article.get_article_tags(article_db.id)
        if current_user:
            is_favorited = await crud_article.is_article_favorited_by_user(
                article_db.id, current_user.id
            )
        else:
            is_favorited = False
        favorites_count = await crud_article.count_article_favorites(article_db.id)
        article_for_reponse = schemas.ArticleForResponse(
            slug=article_db.slug,
            title=article_db.title,
            description=article_db.description,
            body=article_db.body,
            createdAt=article_db.created_at,
            updatedAt=article_db.updated_at,
            author=profile,
            tagList=tags,
            favorited=is_favorited,
            favoritesCount=favorites_count,
        )
        articles.append(article_for_reponse)

    return schemas.MultipleArticlesInResponse(
        articles=articles, articlesCount=len(articles)
    )