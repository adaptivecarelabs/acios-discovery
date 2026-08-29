from __future__ import annotations

from acios_discovery.application.auth.password_hasher import (
    verify_password,
)
from acios_discovery.application.auth.token_service import (
    TokenService,
)
from acios_discovery.domain.repositories.user_repository import (
    UserRepository,
)


class InvalidCredentialsError(Exception):
    """
    Raised when email/password do not match an active user.

    Deliberately does not distinguish "no such user" from "wrong
    password" in its message — that distinction should never be
    exposed to a caller, since it helps an attacker enumerate
    valid emails.
    """


class AuthService:
    """
    Verifies credentials and issues access tokens.
    """

    def __init__(
        self,
        *,
        user_repository: UserRepository,
        token_service: TokenService,
    ) -> None:
        self._user_repository = user_repository
        self._token_service = token_service

    async def login(
        self,
        *,
        email: str,
        password: str,
    ) -> str:
        """
        Verify credentials and return a signed access token.

        Raises InvalidCredentialsError if the email is unknown,
        the account is inactive, or the password is wrong.
        """

        user = await self._user_repository.get_by_email(
            email,
        )

        if user is None or not user.active:
            raise InvalidCredentialsError(
                "Invalid email or password.",
            )

        if not verify_password(
            password,
            user.hashed_password,
        ):
            raise InvalidCredentialsError(
                "Invalid email or password.",
            )

        return self._token_service.create_access_token(
            user_id=user.id,
            role=user.role,
        )
