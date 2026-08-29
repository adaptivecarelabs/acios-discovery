from __future__ import annotations

import pytest

from acios_discovery.application.auth import (
    AuthService,
    InvalidCredentialsError,
    TokenService,
    hash_password,
)
from acios_discovery.domain.user import User, UserId, UserRole


class FakeUserRepository:
    def __init__(self, users: list[User]) -> None:
        self._by_email = {u.email: u for u in users}

    async def get_by_email(self, email: str) -> User | None:
        return self._by_email.get(email)


def make_user(
    *,
    email: str = "user@example.com",
    password: str = "correct-password",
    role: UserRole = UserRole.MEMBER,
    active: bool = True,
) -> User:
    return User(
        id=UserId.from_sequence(1),
        email=email,
        hashed_password=hash_password(password),
        role=role,
        active=active,
    )


@pytest.mark.asyncio
async def test_login_succeeds_with_correct_credentials():
    user = make_user()
    repository = FakeUserRepository([user])
    service = AuthService(
        user_repository=repository,
        token_service=TokenService(secret_key="test-secret"),
    )

    token = await service.login(
        email="user@example.com",
        password="correct-password",
    )

    assert token


@pytest.mark.asyncio
async def test_login_fails_with_wrong_password():
    user = make_user()
    repository = FakeUserRepository([user])
    service = AuthService(
        user_repository=repository,
        token_service=TokenService(secret_key="test-secret"),
    )

    with pytest.raises(InvalidCredentialsError):
        await service.login(
            email="user@example.com",
            password="wrong-password",
        )


@pytest.mark.asyncio
async def test_login_fails_for_unknown_email():
    repository = FakeUserRepository([])
    service = AuthService(
        user_repository=repository,
        token_service=TokenService(secret_key="test-secret"),
    )

    with pytest.raises(InvalidCredentialsError):
        await service.login(
            email="nobody@example.com",
            password="anything",
        )


@pytest.mark.asyncio
async def test_login_fails_for_inactive_user():
    user = make_user(active=False)
    repository = FakeUserRepository([user])
    service = AuthService(
        user_repository=repository,
        token_service=TokenService(secret_key="test-secret"),
    )

    with pytest.raises(InvalidCredentialsError):
        await service.login(
            email="user@example.com",
            password="correct-password",
        )


@pytest.mark.asyncio
async def test_login_error_message_does_not_reveal_which_check_failed():
    """
    "Wrong password" and "no such user" must produce the same
    error, so a caller cannot enumerate valid emails by observing
    different failure messages.
    """
    repository = FakeUserRepository([make_user()])
    service = AuthService(
        user_repository=repository,
        token_service=TokenService(secret_key="test-secret"),
    )

    unknown_email_error = None
    wrong_password_error = None

    try:
        await service.login(email="nobody@example.com", password="x")
    except InvalidCredentialsError as exc:
        unknown_email_error = str(exc)

    try:
        await service.login(
            email="user@example.com",
            password="wrong",
        )
    except InvalidCredentialsError as exc:
        wrong_password_error = str(exc)

    assert unknown_email_error == wrong_password_error
