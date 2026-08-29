from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.domain.repositories.user_repository import (
    UserRepository,
)
from acios_discovery.domain.user import User, UserId, UserRole
from acios_discovery.infrastructure.persistence.orm.user import UserORM


class SqlAlchemyUserRepository(UserRepository):

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def add(
        self,
        user: User,
    ) -> None:

        orm = UserORM(
            id=user.id.value,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role.value,
            active=user.active,
            created_at=user.created_at,
        )

        self._session.add(orm)

    async def get(
        self,
        user_id: UserId,
    ) -> User | None:

        orm = await self._session.get(
            UserORM,
            user_id.value,
        )

        if orm is None:
            return None

        return self._to_domain(orm)

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:

        stmt = select(UserORM).where(
            UserORM.email == email,
        )

        result = await self._session.execute(stmt)

        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return self._to_domain(orm)

    async def list_all(
        self,
    ) -> list[User]:

        stmt = select(UserORM).order_by(UserORM.created_at)

        result = await self._session.execute(stmt)

        rows = result.scalars().all()

        return [self._to_domain(row) for row in rows]

    async def update(
        self,
        user: User,
    ) -> None:

        orm = await self._session.get(
            UserORM,
            user.id.value,
        )

        if orm is None:
            raise ValueError(
                f"User does not exist: {user.id.value}",
            )

        orm.email = user.email
        orm.hashed_password = user.hashed_password
        orm.role = user.role.value
        orm.active = user.active

    @staticmethod
    def _to_domain(orm: UserORM) -> User:
        return User(
            id=UserId.parse(orm.id),
            email=orm.email,
            hashed_password=orm.hashed_password,
            role=UserRole(orm.role),
            active=orm.active,
            created_at=orm.created_at,
        )
