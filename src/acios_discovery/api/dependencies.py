from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.application.auth import (
    InvalidTokenError,
    TokenService,
)
from acios_discovery.domain.user import User, UserRole
from acios_discovery.infrastructure.persistence.config import JWT_SECRET_KEY
from acios_discovery.infrastructure.persistence.database import (
    SessionFactory,
)
from acios_discovery.infrastructure.persistence.repositories.user_repository import (
    SqlAlchemyUserRepository,
)

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_token_service = TokenService(secret_key=JWT_SECRET_KEY)


def get_token_service() -> TokenService:
    return _token_service


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with SessionFactory() as session:
        yield session


async def get_current_user(
    token: str = Depends(_oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    """
    Resolves the authenticated user from the bearer token.

    Raises 401 if the token is missing, invalid, expired, or no
    longer corresponds to an active user (e.g. deactivated after
    the token was issued).
    """

    try:
        payload = _token_service.verify_access_token(token)

    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    repository = SqlAlchemyUserRepository(session)

    user = await repository.get(payload.user_id)

    if user is None or not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer active.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def require_admin(
    user: User = Depends(get_current_user),
) -> User:

    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    return user
