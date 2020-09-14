from typing import Dict, List

from fastapi import APIRouter, Body, HTTPException

from app import schemas
from app.core import security
from app.crud import users as crud_user

router = APIRouter()


@router.get("", tags=["users"])
async def read_users() -> List[Dict[str, str]]:
    return [{"username": "Foo"}, {"username": "Bar"}]


@router.get("/me", tags=["users"])
async def read_user_me() -> Dict[str, str]:
    return {"username": "fakecurrentuser"}


@router.get("{username}", tags=["users"])
async def read_user(username: str) -> Dict[str, str]:
    return {"username": username}


@router.post(
    "",
    name="Register a new user",
    description="Register a new user",
    response_model=schemas.UserResponse,
)
async def register(
    user_in: schemas.UserCreate = Body(..., embed=True, alias="user"),
) -> schemas.UserResponse:
    user = await crud_user.get_user_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user_id = await crud_user.create(user_in)

    token = security.create_access_token(user_id)
    return schemas.UserResponse(
        user=schemas.UserWithToken(
            username=user_in.username,
            email=user_in.email,
            bio=user_in.bio,
            image=user_in.image,
            token=token,
        )
    )
