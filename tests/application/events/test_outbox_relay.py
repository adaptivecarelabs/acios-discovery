from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from acios_discovery.application.events.outbox import OutboxMessage
from acios_discovery.application.events.outbox_relay import OutboxRelay
from acios_discovery.application.events.outbox_repository import (
    OutboxRepository,
)
from acios_discovery.domain.events.event_publisher import EventPublisher


def make_message(
    event_type: str = "CompanyDiscoveredEvent",
) -> OutboxMessage:

    now = datetime.now(UTC)

    return OutboxMessage(
        id=uuid4(),
        event_type=event_type,
        aggregate_type="discovery",
        aggregate_id=None,
        payload={"example": "payload"},
        occurred_at=now,
        created_at=now,
    )


class FakeOutboxRepository(OutboxRepository):

    def __init__(
        self,
        *,
        messages: list[OutboxMessage],
    ) -> None:

        self._messages = messages

        self.published_ids: list[UUID] = []

        self.failed: list[tuple[UUID, str]] = []

        self.dead_lettered: list[UUID] = []

    async def add(
        self,
        message: OutboxMessage,
    ) -> None:
        self._messages.append(message)

    async def get_unpublished(
        self,
        *,
        limit: int = 100,
    ) -> list[OutboxMessage]:
        return list(self._messages[:limit])

    async def mark_published(
        self,
        message_id: UUID,
    ) -> None:
        self.published_ids.append(message_id)

    async def mark_failed(
        self,
        message_id: UUID,
        error: str,
    ) -> None:
        self.failed.append((message_id, error))

    async def mark_dead_lettered(self, message_id) -> None:
        self.dead_lettered.append(message_id)


class RecordingPublisher(EventPublisher):

    def __init__(self) -> None:
        self.published: list[OutboxMessage] = []

    async def publish(
        self,
        message: OutboxMessage,
    ) -> None:
        self.published.append(message)


class FailingPublisher(EventPublisher):
    """
    Fails to publish messages whose event_type is in
    `fail_for`, succeeds for everything else.
    """

    def __init__(
        self,
        *,
        fail_for: set[str],
    ) -> None:
        self._fail_for = fail_for
        self.published: list[OutboxMessage] = []

    async def publish(
        self,
        message: OutboxMessage,
    ) -> None:

        if message.event_type in self._fail_for:
            raise RuntimeError(
                f"Simulated failure for {message.event_type}",
            )

        self.published.append(message)


@pytest.mark.asyncio
async def test_relay_publishes_all_messages_and_marks_them_published():

    messages = [
        make_message("CompanyDiscoveredEvent"),
        make_message("CompanyMergedEvent"),
    ]

    repository = FakeOutboxRepository(messages=messages)
    publisher = RecordingPublisher()

    relay = OutboxRelay(
        repository=repository,
        publisher=publisher,
    )

    published_count = await relay.poll_once()

    assert published_count == 2

    assert len(publisher.published) == 2

    assert repository.published_ids == [
        messages[0].id,
        messages[1].id,
    ]

    assert repository.failed == []


@pytest.mark.asyncio
async def test_relay_continues_past_a_failed_message():

    messages = [
        make_message("CompanyDiscoveredEvent"),
        make_message("CompanyMergedEvent"),
    ]

    repository = FakeOutboxRepository(messages=messages)

    publisher = FailingPublisher(
        fail_for={"CompanyDiscoveredEvent"},
    )

    relay = OutboxRelay(
        repository=repository,
        publisher=publisher,
    )

    published_count = await relay.poll_once()

    # Only the second message succeeded.
    assert published_count == 1

    assert len(publisher.published) == 1
    assert publisher.published[0].event_type == "CompanyMergedEvent"

    # The first message was marked failed, not published.
    assert repository.published_ids == [messages[1].id]

    assert len(repository.failed) == 1
    assert repository.failed[0][0] == messages[0].id
    assert "Simulated failure" in repository.failed[0][1]


@pytest.mark.asyncio
async def test_relay_respects_batch_size():

    messages = [
        make_message() for _ in range(5)
    ]

    repository = FakeOutboxRepository(messages=messages)
    publisher = RecordingPublisher()

    relay = OutboxRelay(
        repository=repository,
        publisher=publisher,
        batch_size=3,
    )

    published_count = await relay.poll_once()

    assert published_count == 3

    assert len(publisher.published) == 3


@pytest.mark.asyncio
async def test_relay_returns_zero_when_nothing_unpublished():

    repository = FakeOutboxRepository(messages=[])
    publisher = RecordingPublisher()

    relay = OutboxRelay(
        repository=repository,
        publisher=publisher,
    )

    published_count = await relay.poll_once()

    assert published_count == 0
    assert publisher.published == []
