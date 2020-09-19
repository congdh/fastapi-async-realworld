from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app import schemas
from app.api import deps
from app.crud import crud_profile

router = APIRouter()


@router.get(
    "/{username}",
    name="Get a profile",
    description="Get a profile of a user of the system. Auth is optional",
    response_model=schemas.ProfileResponse,
)
async def get_profile(
    username: str,
    requested_user: schemas.UserDB = Depends(deps.get_current_user(required=False)),
) -> schemas.ProfileResponse:
    profile = await crud_profile.get_profile_by_username(
        username, requested_user=requested_user
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user not existed",
        )
    return schemas.ProfileResponse(profile=profile)
