from typing import Dict, List

from fastapi import APIRouter

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
