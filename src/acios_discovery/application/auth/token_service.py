from __future__ import annotations

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from acios_discovery.domain.user import UserId, UserRole

ALGORITHM = "HS256"
DEFAULT_EXPIRY_MINUTES = 60 * 12  # 12 hours


class InvalidTokenError(Exception):
    """
    Raised when a JWT is missing, malformed, expired, or fails
    signature verification.
    """


class TokenPayload:
    """
    Decoded, validated contents of an access token.
    """

    __slots__ = ("user_id", "role")

    def __init__(
        self,
        *,
        user_id: UserId,
        role: UserRole,
    ) -> None:
        self.user_id = user_id
        self.role = role


class TokenService:
    """
    Issues and verifies JWT access tokens.

    Uses HS256 (symmetric signing) — appropriate for a single
    trusted backend issuing and verifying its own tokens for a
    small internal team. Would need to move to RS256 (asymmetric)
    if multiple independent services ever need to verify tokens
    without sharing the signing secret.
    """

    def __init__(
        self,
        *,
        secret_key: str,
        expiry_minutes: int = DEFAULT_EXPIRY_MINUTES,
    ) -> None:
        self._secret_key = secret_key
        self._expiry_minutes = expiry_minutes

    def create_access_token(
        self,
        *,
        user_id: UserId,
        role: UserRole,
    ) -> str:

        now = datetime.now(UTC)

        payload = {
            "sub": user_id.value,
            "role": role.value,
            "iat": now,
            "exp": now + timedelta(minutes=self._expiry_minutes),
        }

        return jwt.encode(
            payload,
            self._secret_key,
            algorithm=ALGORITHM,
        )

    def verify_access_token(
        self,
        token: str,
    ) -> TokenPayload:

        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[ALGORITHM],
            )

        except JWTError as exc:
            raise InvalidTokenError(
                f"Invalid or expired token: {exc}",
            ) from exc

        try:
            user_id = UserId.parse(payload["sub"])
            role = UserRole(payload["role"])

        except (KeyError, ValueError) as exc:
            raise InvalidTokenError(
                f"Malformed token payload: {exc}",
            ) from exc

        return TokenPayload(
            user_id=user_id,
            role=role,
        )
