from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from acios_discovery.application.events.outbox import OutboxMessage
from acios_discovery.application.events.outbox_relay import OutboxRelay
from acios_discovery.application.events.outbox_repository import (
    OutboxRepository,
)
from acios_discovery.domain.events.event_publisher import EventPublisher


def make_message(attempts: int) -> OutboxMessage:
    now = datetime.now(UTC)

    return OutboxMessage(
        id=uuid4(),
        event_type="TestEvent",
        aggregate_type="test",
        aggregate_id=None,
        payload={},
        occurred_at=now,
        created_at=now,
        attempts=attempts,
    )


class FakeOutboxRepository(OutboxRepository):

    def __init__(self, *, messages) -> None:
        self._messages = messages
        self.published_ids = []
        self.failed = []
        self.dead_lettered = []

    async def add(self, message) -> None:
        self._messages.append(message)

    async def get_unpublished(self, *, limit: int = 100):
        return list(self._messages[:limit])

    async def mark_published(self, message_id) -> None:
        self.published_ids.append(message_id)

    async def mark_failed(self, message_id, error: str) -> None:
        self.failed.append((message_id, error))

    async def mark_dead_lettered(self, message_id) -> None:
        self.dead_lettered.append(message_id)


class RecordingPublisher(EventPublisher):

    def __init__(self) -> None:
        self.published = []

    async def publish(self, message) -> None:
        self.published.append(message)


@pytest.mark.asyncio
async def test_relay_skips_exhausted_messages_without_publishing():

    exhausted = make_message(attempts=5)
    fresh = make_message(attempts=1)

    repository = FakeOutboxRepository(messages=[exhausted, fresh])
    publisher = RecordingPublisher()

    relay = OutboxRelay(
        repository=repository,
        publisher=publisher,
        max_attempts=5,
    )

    published_count = await relay.poll_once()

    # Only the fresh message was actually attempted.
    assert published_count == 1
    assert len(publisher.published) == 1
    assert publisher.published[0].id == fresh.id

    assert repository.published_ids == [fresh.id]

    # The exhausted message was neither published nor marked
    # failed again — it was simply skipped this cycle.
    assert repository.failed == []
    assert repository.dead_lettered == [exhausted.id]
