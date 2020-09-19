from fastapi import APIRouter

from app.api.routers import authentication, profiles, users

api_router = APIRouter()

api_router.include_router(
    authentication.router, tags=["User and Authentication"], prefix="/users"
)
api_router.include_router(
    users.router, tags=["User and Authentication"], prefix="/user"
)
api_router.include_router(profiles.router, tags=["Profiles"], prefix="/profiles")
