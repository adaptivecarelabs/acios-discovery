from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.api.dependencies import (
    get_current_user,
    get_db_session,
    get_token_service,
)
from acios_discovery.application.auth import (
    AuthService,
    InvalidCredentialsError,
    TokenService,
)
from acios_discovery.domain.user import User
from acios_discovery.infrastructure.persistence.repositories.user_repository import (
    SqlAlchemyUserRepository,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(BaseModel):
    id: str
    email: str
    role: str


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session),
    token_service: TokenService = Depends(get_token_service),
) -> TokenResponse:
    """
    Exchanges email + password for a bearer access token.

    Uses the standard OAuth2 password-flow form fields (username,
    password) — `username` is the account's email address.
    """

    repository = SqlAlchemyUserRepository(session)

    auth_service = AuthService(
        user_repository=repository,
        token_service=token_service,
    )

    try:
        token = await auth_service.login(
            email=form_data.username,
            password=form_data.password,
        )

    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return TokenResponse(access_token=token)


@router.get("/me", response_model=CurrentUserResponse)
async def get_me(
    user: User = Depends(get_current_user),
) -> CurrentUserResponse:
    return CurrentUserResponse(
        id=user.id.value,
        email=user.email,
        role=user.role.value,
    )
