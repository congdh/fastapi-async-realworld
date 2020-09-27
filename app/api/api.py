from fastapi import APIRouter

from app.api.routers import articles, authentication, comments, profiles, tags, users

api_router = APIRouter()

api_router.include_router(
    authentication.router, tags=["User and Authentication"], prefix="/users"
)
api_router.include_router(
    users.router, tags=["User and Authentication"], prefix="/user"
)
api_router.include_router(profiles.router, tags=["Profiles"], prefix="/profiles")
api_router.include_router(tags.router, tags=["Tags"], prefix="/tags")
api_router.include_router(articles.router, tags=["Articles"], prefix="/articles")
api_router.include_router(
    comments.router, tags=["Comments"], prefix="/articles/{slug}/comments"
)
