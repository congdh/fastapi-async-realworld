from typing import Optional

from pydantic import BaseModel, EmailStr, Field, SecretStr


class UserBase(BaseModel):
    email: Optional[EmailStr] = Field(None, example="sheilaavery@yahoo.com")
    username: Optional[str] = Field(None, example="perryshari")
    bio: Optional[str] = None
    image: Optional[str] = None


class UserDB(UserBase):
    id: int
    hashed_password: str


class UserCreate(UserBase):
    email: EmailStr = Field(..., example="sheilaavery@yahoo.com")
    username: str = Field(..., example="perryshari")
    password: SecretStr = Field(..., example="changeit")


class UserWithToken(UserBase):
    token: str = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1OTk3MjI3MTIsInN1YiI6IjEifQ.cTWIopIYrXLEeRix_sTiqx6RRBuXG4a6xVUcMKyovWA",  # noqa
    )


class UserResponse(BaseModel):
    user: UserWithToken


class LoginUser(BaseModel):
    email: str
    password: SecretStr

    class Config:
        schema_extra = {
            "example": {
                "email": "ahart@yahoo.com",
                "password": "changeit",
            }
        }
