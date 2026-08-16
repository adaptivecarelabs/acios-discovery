from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.application.events.outbox import OutboxMessage
from acios_discovery.infrastructure.persistence.repositories.outbox_repository import (
    SqlAlchemyOutboxRepository,
)


def make_message(
    *,
    event_type: str = "JobCompletedEvent",
    aggregate_type: str = "crawl",
    aggregate_id: str | None = None,
    created_at: datetime | None = None,
) -> OutboxMessage:
    now = datetime.now(UTC)

    return OutboxMessage(
        id=uuid4(),
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        payload={
            "pages_crawled": 2,
            "companies_discovered": 10,
        },
        occurred_at=now,
        created_at=created_at or now,
    )


def make_repository(
    db_session: AsyncSession,
) -> SqlAlchemyOutboxRepository:
    return SqlAlchemyOutboxRepository(
        db_session,
    )


@pytest.mark.asyncio
async def test_add_and_get_unpublished(
    db_session: AsyncSession,
) -> None:
    repository = make_repository(db_session)

    message = make_message()

    await repository.add(message)
    await db_session.flush()

    messages = await repository.get_unpublished()

    assert len(messages) == 1

    stored = messages[0]

    assert stored.id == message.id
    assert stored.event_type == "JobCompletedEvent"
    assert stored.aggregate_type == "crawl"
    assert stored.payload == {
        "pages_crawled": 2,
        "companies_discovered": 10,
    }


@pytest.mark.asyncio
async def test_get_unpublished_returns_oldest_first(
    db_session: AsyncSession,
) -> None:
    repository = make_repository(db_session)

    base_time = datetime.now(UTC)

    older = make_message(
        event_type="OlderEvent",
        created_at=base_time,
    )

    newer = make_message(
        event_type="NewerEvent",
        created_at=base_time + timedelta(seconds=1),
    )

    await repository.add(newer)
    await repository.add(older)
    await db_session.flush()

    messages = await repository.get_unpublished()

    assert [message.event_type for message in messages] == [
        "OlderEvent",
        "NewerEvent",
    ]


@pytest.mark.asyncio
async def test_get_unpublished_respects_limit(
    db_session: AsyncSession,
) -> None:
    repository = make_repository(db_session)

    for index in range(3):
        await repository.add(
            make_message(
                event_type=f"Event{index}",
            )
        )

    await db_session.flush()

    messages = await repository.get_unpublished(
        limit=2,
    )

    assert len(messages) == 2


@pytest.mark.asyncio
async def test_mark_published_removes_message_from_unpublished(
    db_session: AsyncSession,
) -> None:
    repository = make_repository(db_session)

    message = make_message()

    await repository.add(message)
    await db_session.flush()

    assert len(
        await repository.get_unpublished()
    ) == 1

    await repository.mark_published(
        message.id,
    )

    await db_session.flush()

    messages = await repository.get_unpublished()

    assert messages == []


@pytest.mark.asyncio
async def test_mark_failed_increments_attempts_and_stores_error(
    db_session: AsyncSession,
) -> None:
    repository = make_repository(db_session)

    message = make_message()

    await repository.add(message)
    await db_session.flush()

    await repository.mark_failed(
        message.id,
        "Connection refused",
    )

    await db_session.flush()

    messages = await repository.get_unpublished()

    assert len(messages) == 1

    stored = messages[0]

    assert stored.id == message.id

    from sqlalchemy import select

    from acios_discovery.infrastructure.persistence.orm.outbox_event import (
        OutboxEventORM,
    )

    result = await db_session.execute(
        select(OutboxEventORM).where(
            OutboxEventORM.id == message.id,
        )
    )

    row = result.scalar_one()

    assert row.attempts == 1
    assert row.last_error == "Connection refused"


@pytest.mark.asyncio
async def test_mark_published_missing_message_raises(
    db_session: AsyncSession,
) -> None:
    repository = make_repository(db_session)

    missing_id = uuid4()

    with pytest.raises(
        ValueError,
        match="Outbox event does not exist",
    ):
        await repository.mark_published(
            missing_id,
        )


@pytest.mark.asyncio
async def test_mark_failed_missing_message_raises(
    db_session: AsyncSession,
) -> None:
    repository = make_repository(db_session)

    missing_id = uuid4()

    with pytest.raises(
        ValueError,
        match="Outbox event does not exist",
    ):
        await repository.mark_failed(
            missing_id,
            "Something failed",
        )
