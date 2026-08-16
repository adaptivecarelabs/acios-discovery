from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from acios_discovery.application.events.event_serializer import (
    serialize_event,
)
from acios_discovery.application.events.outbox import OutboxMessage
from acios_discovery.application.events.outbox_repository import (
    OutboxRepository,
)
from acios_discovery.domain.events.crawl_event import CrawlEvent


class OutboxService:
    def __init__(
        self,
        repository: OutboxRepository,
    ) -> None:
        self._repository = repository

    async def record(
        self,
        event: CrawlEvent,
    ) -> None:
        message = OutboxMessage(
            id=uuid4(),
            event_type=type(event).__name__,
            aggregate_type="crawl",
            aggregate_id=None,
            payload=serialize_event(event),
            occurred_at=event.occurred_at,
            created_at=datetime.now(UTC),
        )

        await self._repository.add(
            message,
        )
