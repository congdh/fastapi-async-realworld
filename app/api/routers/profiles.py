from fastapi import APIRouter, HTTPException
from starlette import status

from app import schemas
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
) -> schemas.ProfileResponse:
    profile = await crud_profile.get_profile_by_username(username)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user not existed",
        )
    return schemas.ProfileResponse(profile=profile)
