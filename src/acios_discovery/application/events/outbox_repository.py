from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from acios_discovery.application.events.outbox import OutboxMessage


class OutboxRepository(ABC):

    @abstractmethod
    async def add(
        self,
        message: OutboxMessage,
    ) -> None:
        ...

    @abstractmethod
    async def get_unpublished(
        self,
        *,
        limit: int = 100,
    ) -> list[OutboxMessage]:
        ...

    @abstractmethod
    async def mark_published(
        self,
        message_id: UUID,
    ) -> None:
        ...

    @abstractmethod
    async def mark_failed(
        self,
        message_id: UUID,
        error: str,
    ) -> None:
        ...

    @abstractmethod
    async def mark_dead_lettered(
        self,
        message_id: UUID,
    ) -> None:
        ...
