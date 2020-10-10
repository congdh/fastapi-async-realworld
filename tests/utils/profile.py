from app import schemas


def assert_profile_with_user(
    expected: schemas.UserDB,
    actual: schemas.Profile,
) -> None:
    assert actual.username == expected.username
    assert actual.bio == expected.bio
    assert actual.image == expected.image
