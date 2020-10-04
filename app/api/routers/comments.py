from fastapi import APIRouter, Body, Depends, HTTPException
from starlette import status

from app import schemas
from app.api import deps
from app.crud import crud_article, crud_comment, crud_profile

SLUG_NOT_FOUND = "article with this slug not found"

router = APIRouter()


@router.post(
    "",
    name="Create a comment for an article",
    description="Create a comment for an article. Auth is required",
    response_model=schemas.CommentInResponse,
)
async def create_article_comment(
    slug: str,
    comment_in: schemas.CommentInCreate = Body(..., embed=True, alias="comment"),
    current_user: schemas.UserDB = Depends(deps.get_current_user()),
) -> schemas.CommentInResponse:
    article_db = await crud_article.get_article_by_sluq(slug=slug)
    if article_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=SLUG_NOT_FOUND,
        )
    comment_id = await crud_comment.create(
        payload=comment_in, article_id=article_db.id, author_id=current_user.id
    )
    comment_db = await crud_comment.get(comment_id)  # type: ignore
    if comment_db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something wrong. This comment has created but not existed",
        )
    profile = await crud_profile.get_profile_by_user_id(
        comment_db.author_id, requested_user=current_user
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This article's author not existed",
        )
    return schemas.CommentInResponse(
        comment=schemas.CommentForResponse(
            id=comment_db.id,
            body=comment_db.body,
            createdAt=comment_db.created_at,
            updatedAt=comment_db.updated_at,
            author=profile,
        )
    )


@router.get(
    "",
    name="Get comments for an article",
    description="Get the comments for an article. Auth is optional",
    response_model=schemas.MultipleCommentsInResponse,
)
async def get_comments_from_an_article(
    slug: str,
    current_user: schemas.UserDB = Depends(deps.get_current_user(required=False)),
) -> schemas.MultipleCommentsInResponse:
    article_db = await crud_article.get_article_by_sluq(slug=slug)
    if article_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="article with this slug not found",
        )
    comment_dbs = await crud_comment.get_comments_from_an_article(
        article_id=article_db.id
    )
    comments = []
    for comment_db in comment_dbs:
        profile = await crud_profile.get_profile_by_user_id(
            comment_db.author_id, requested_user=current_user
        )
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This article's author not existed",
            )
        comments.append(
            schemas.CommentForResponse(
                id=comment_db.id,
                body=comment_db.body,
                createdAt=comment_db.created_at,
                updatedAt=comment_db.updated_at,
                author=profile,
            )
        )
    return schemas.MultipleCommentsInResponse(comments=comments)


@router.delete(
    "/{comment_id}",
    name="Delete a comment for an article",
    description="Delete a comment for an article. Auth is required",
)
async def delete_comment_for_article(
    slug: str,
    comment_id: int,
    current_user: schemas.UserDB = Depends(deps.get_current_user()),
) -> None:

    article_db = await crud_article.get_article_by_sluq(slug=slug)
    if article_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=SLUG_NOT_FOUND,
        )
    comment_db = await crud_comment.get(comment_id)
    if comment_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="comment with this id not found",
        )
    if comment_db.article_id != article_db.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This comment is not belong to this article",
        )
    if comment_db.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can not delete a comment is not belong to yourself",
        )
    await crud_comment.delete(comment_id)
