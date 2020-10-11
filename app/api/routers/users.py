from fastapi import APIRouter, Body, Depends, HTTPException
from starlette import status
from starlette.status import HTTP_400_BAD_REQUEST

from app import schemas
from app.api import deps
from app.core import security
from app.crud import crud_user

router = APIRouter()


@router.get(
    "",
    name="Get current user",
    description="Gets the currently logged-in user",
    response_model=schemas.UserResponse,
)
async def retrieve_current_user(
    current_user: schemas.UserDB = Depends(deps.get_current_user()),
) -> schemas.UserResponse:
    token = security.create_access_token(current_user.id)
    return schemas.UserResponse(
        user=schemas.UserWithToken(
            username=current_user.username,
            email=current_user.email,
            bio=current_user.bio,
            image=current_user.image,
            token=token,
        )
    )


@router.put(
    "",
    name="Update current user",
    description="Updated user information for current user",
    response_model=schemas.UserResponse,
)
async def update_current_user(
    user_update: schemas.UserUpdate = Body(..., embed=True, alias="user"),
    current_user: schemas.UserDB = Depends(deps.get_current_user()),
) -> schemas.UserResponse:
    if user_update.username and user_update.username != current_user.username:
        user_db = await crud_user.get_user_by_username(username=user_update.username)
        if user_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user with this username already exists",
            )
    if user_update.email and user_update.email != current_user.email:
        user_db = await crud_user.get_user_by_email(email=user_update.email)
        if user_db:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="user with this email already exists",
            )
    user_id = await crud_user.update(user_id=current_user.id, payload=user_update)
    user_db = await crud_user.get(user_id)
    token = security.create_access_token(current_user.id)
    return schemas.UserResponse(
        user=schemas.UserWithToken(
            username=user_db.username,  # type: ignore
            email=user_db.email,  # type: ignore
            bio=user_db.bio,  # type: ignore
            image=user_db.image,  # type: ignore
            token=token,
        )
    )
