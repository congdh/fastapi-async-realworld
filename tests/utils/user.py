from faker import Faker
from pydantic import SecretStr

from app import schemas
from app.crud import users as crud_user

TEST_USER_PASSWORD = "changeit"


async def get_test_user() -> schemas.UserDB:
    faker = Faker()
    profile = faker.profile()
    TEST_USER_EMAIL = profile.get("mail", None)
    TEST_USER_USERNAME = profile.get("username", None)
    user_row = await crud_user.get_user_by_email(email=TEST_USER_EMAIL)
    if user_row is None:
        user_in = schemas.UserCreate(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=SecretStr(TEST_USER_PASSWORD),
        )
        user_id = await crud_user.create(payload=user_in)
        user_row = await crud_user.get(user_id)
    return schemas.UserDB(**user_row)


# def get_test_user_token(test_user: models.User) -> str:
#     return security.create_access_token(test_user.id)
