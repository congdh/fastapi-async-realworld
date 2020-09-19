from typing import Optional

from pydantic import BaseModel


class Profile(BaseModel):
    username: str
    bio: Optional[str] = None
    image: Optional[str] = None
    following: bool = False


class ProfileResponse(BaseModel):
    profile: Profile
