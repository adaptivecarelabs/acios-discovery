from __future__ import annotations

from abc import ABC, abstractmethod

from acios_discovery.domain.user import User


class UserRepository(ABC):
    """
    Domain repository interface for users.
    """

    @abstractmethod
    async def add(
        self,
        user: User,
    ) -> None:
        ...

    @abstractmethod
    async def get(
        self,
        user_id,
    ) -> User | None:
        ...

    @abstractmethod
    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        ...

    @abstractmethod
    async def list_all(
        self,
    ) -> list[User]:
        ...

    @abstractmethod
    async def update(
        self,
        user: User,
    ) -> None:
        ...
