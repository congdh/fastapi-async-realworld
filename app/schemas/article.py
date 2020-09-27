import datetime
from typing import List, Optional

from pydantic import BaseModel

from app import schemas


class ArticleBase(BaseModel):
    title: str
    description: str
    body: str


class ArticleDB(ArticleBase):
    id: int
    slug: str
    author_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ArticleInCreate(BaseModel):
    title: str
    description: str
    body: str
    tagList: Optional[List[str]]


class ArticleForResponse(ArticleBase):
    slug: str
    author: schemas.Profile
    createdAt: datetime.datetime
    updatedAt: datetime.datetime
    tagList: Optional[List[str]]
    favorited: bool
    favoritesCount: int


class ArticleInResponse(BaseModel):
    article: ArticleForResponse


class ArticleInUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    body: Optional[str]
    tagList: Optional[List[str]]


class MultipleArticlesInResponse(BaseModel):
    articles: List[ArticleForResponse]
    articlesCount: int
