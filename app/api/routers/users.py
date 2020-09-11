from fastapi import APIRouter

router = APIRouter()


@router.get("", tags=["users"])
async def read_users():
    return [{"username": "Foo"}, {"username": "Bar"}]


@router.get("/me", tags=["users"])
async def read_user_me():
    return {"username": "fakecurrentuser"}


@router.get("{username}", tags=["users"])
async def read_user(username: str):
    return {"username": username}
