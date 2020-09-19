from typing import List

from fastapi import APIRouter

from app.crud import crud_tag

router = APIRouter()


@router.get(
    "",
    name="Get tags",
    description="Get tags. Auth not required",
    response_model=List[str],
)
async def list_all_tags() -> List[str]:
    tags = await crud_tag.get_all_tags()
    return tags
