from fastapi import APIRouter, Body, HTTPException

from app import schemas
from app.core import security
from app.crud import crud_user

router = APIRouter()


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


@router.post(
    "/login",
    name="Login and Remember Token",
    description="Login for existing user",
    response_model=schemas.UserResponse,
)
async def login(
    user_login: schemas.LoginUser = Body(
        ..., embed=True, alias="user", name="Credentials to use"
    ),
) -> schemas.UserResponse:
    user = await crud_user.authenticate(
        email=user_login.email, password=user_login.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token = security.create_access_token(user.id)
    return schemas.UserResponse(
        user=schemas.UserWithToken(
            username=user.username,
            email=user.email,
            bio=user.bio,
            image=user.image,
            token=token,
        )
    )
