import datetime
from typing import List

from pydantic import BaseModel

from app import schemas


class CommentBase(BaseModel):
    body: str


class CommentDB(CommentBase):
    id: int
    author_id: int
    article_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class CommentInCreate(CommentBase):
    pass


class CommentForResponse(CommentBase):
    id: int
    createdAt: datetime.datetime
    updatedAt: datetime.datetime
    author: schemas.Profile


class CommentInResponse(BaseModel):
    comment: CommentForResponse


class MultipleCommentsInResponse(BaseModel):
    comments: List[CommentForResponse]
    pass
