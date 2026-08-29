from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.api.dependencies import get_db_session, require_admin
from acios_discovery.api.schemas.user import (
    CreateUserRequest,
    UpdateUserRequest,
    UserResponse,
)
from acios_discovery.application.auth import hash_password
from acios_discovery.domain.user import User, UserId, UserRole
from acios_discovery.infrastructure.persistence.repositories.user_repository import (
    SqlAlchemyUserRepository,
)

router = APIRouter(prefix="/users", tags=["users"])


def _to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id.value,
        email=user.email,
        role=user.role.value,
        active=user.active,
        created_at=user.created_at,
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    request: CreateUserRequest,
    _admin: User = Depends(require_admin),
    db_session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    """
    Creates a new user account. Admin only.
    """

    repository = SqlAlchemyUserRepository(db_session)

    existing = await repository.get_by_email(request.email)

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    try:
        role = UserRole(request.role)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid role '{request.role}'. "
                f"Must be one of: {[r.value for r in UserRole]}"
            ),
        ) from exc

    existing_users = await repository.list_all()

    next_sequence = len(existing_users) + 1

    user = User(
        id=UserId.from_sequence(next_sequence),
        email=request.email,
        hashed_password=hash_password(request.password),
        role=role,
    )

    await repository.add(user)

    await db_session.commit()

    return _to_response(user)


@router.get("", response_model=list[UserResponse])
async def list_users(
    _admin: User = Depends(require_admin),
    db_session: AsyncSession = Depends(get_db_session),
) -> list[UserResponse]:
    """
    Lists all user accounts. Admin only.
    """

    repository = SqlAlchemyUserRepository(db_session)

    users = await repository.list_all()

    return [_to_response(u) for u in users]


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    _admin: User = Depends(require_admin),
    db_session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    """
    Updates a user's role or active status. Admin only.

    Used to deactivate an account (active=false) rather than
    deleting it, preserving crawl-session attribution history.
    """

    repository = SqlAlchemyUserRepository(db_session)

    user = await repository.get(UserId.parse(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such user.",
        )

    if request.role is not None:
        try:
            user.role = UserRole(request.role)

        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid role '{request.role}'. "
                    f"Must be one of: {[r.value for r in UserRole]}"
                ),
            ) from exc

    if request.active is not None:
        user.active = request.active

    await repository.update(user)

    await db_session.commit()

    return _to_response(user)
