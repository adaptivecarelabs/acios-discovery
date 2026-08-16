from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.application.events.outbox import OutboxMessage
from acios_discovery.application.events.outbox_repository import (
    OutboxRepository,
)
from acios_discovery.infrastructure.persistence.orm.outbox_event import (
    OutboxEventORM,
)


class SqlAlchemyOutboxRepository(
    OutboxRepository,
):
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def add(
        self,
        message: OutboxMessage,
    ) -> None:
        self._session.add(
            OutboxEventORM(
                id=message.id,
                event_type=message.event_type,
                aggregate_type=message.aggregate_type,
                aggregate_id=message.aggregate_id,
                payload=message.payload,
                occurred_at=message.occurred_at,
                created_at=message.created_at,
                attempts=0,
            )
        )

    async def get_unpublished(
        self,
        *,
        limit: int = 100,
    ) -> list[OutboxMessage]:

        stmt = (
            select(OutboxEventORM)
            .where(
                OutboxEventORM.published_at.is_(None)
            )
            .order_by(
                OutboxEventORM.created_at,
            )
            .limit(limit)
        )

        result = await self._session.execute(
            stmt,
        )

        rows = result.scalars().all()

        return [
            OutboxMessage(
                id=row.id,
                event_type=row.event_type,
                aggregate_type=row.aggregate_type,
                aggregate_id=row.aggregate_id,
                payload=row.payload,
                occurred_at=row.occurred_at,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def mark_published(
        self,
        message_id: UUID,
    ) -> None:
        stmt = select(
            OutboxEventORM,
        ).where(
            OutboxEventORM.id == message_id,
        )

        result = await self._session.execute(
            stmt,
        )

        row = result.scalar_one_or_none()

        if row is None:
            raise ValueError(
                f"Outbox event does not exist: {message_id}"
            )

        row.published_at = datetime.now(UTC)

    async def mark_failed(
        self,
        message_id: UUID,
        error: str,
    ) -> None:
        stmt = select(
            OutboxEventORM,
        ).where(
            OutboxEventORM.id == message_id,
        )

        result = await self._session.execute(
            stmt,
        )

        row = result.scalar_one_or_none()

        if row is None:
            raise ValueError(
                f"Outbox event does not exist: {message_id}"
            )

        row.attempts += 1
        row.last_error = error
