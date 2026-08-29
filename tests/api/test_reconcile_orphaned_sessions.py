from __future__ import annotations

import pytest

from acios_discovery.api.crawl_manager import reconcile_orphaned_sessions
from acios_discovery.domain.crawling.crawl_session import CrawlSession
from acios_discovery.domain.crawling.crawl_session_status import (
    CrawlSessionStatus,
)
from acios_discovery.infrastructure.persistence.repositories.crawl_session_repository import (
    SqlAlchemyCrawlSessionRepository,
)


@pytest.mark.asyncio
async def test_reconcile_marks_running_sessions_as_cancelled(
    test_session_factory,
) -> None:

    async with test_session_factory() as session:
        repository = SqlAlchemyCrawlSessionRepository(session)

        running_session = CrawlSession(
            id="orphaned-session-1",
            status=CrawlSessionStatus.RUNNING,
            state="TestState",
        )

        await repository.save(running_session)
        await session.commit()

    reconciled_count = await reconcile_orphaned_sessions(
        session_factory=test_session_factory,
    )

    assert reconciled_count == 1

    async with test_session_factory() as session:
        repository = SqlAlchemyCrawlSessionRepository(session)
        reloaded = await repository.get("orphaned-session-1")

    assert reloaded.status == CrawlSessionStatus.CANCELLED


@pytest.mark.asyncio
async def test_reconcile_does_not_touch_completed_or_failed_sessions(
    test_session_factory,
) -> None:

    async with test_session_factory() as session:
        repository = SqlAlchemyCrawlSessionRepository(session)

        completed = CrawlSession(
            id="completed-session",
            status=CrawlSessionStatus.COMPLETED,
        )
        failed = CrawlSession(
            id="failed-session",
            status=CrawlSessionStatus.FAILED,
        )
        pending = CrawlSession(
            id="pending-session",
            status=CrawlSessionStatus.PENDING,
        )

        await repository.save(completed)
        await repository.save(failed)
        await repository.save(pending)
        await session.commit()

    reconciled_count = await reconcile_orphaned_sessions(
        session_factory=test_session_factory,
    )

    assert reconciled_count == 0

    async with test_session_factory() as session:
        repository = SqlAlchemyCrawlSessionRepository(session)

        assert (
            await repository.get("completed-session")
        ).status == CrawlSessionStatus.COMPLETED
        assert (
            await repository.get("failed-session")
        ).status == CrawlSessionStatus.FAILED
        assert (
            await repository.get("pending-session")
        ).status == CrawlSessionStatus.PENDING


@pytest.mark.asyncio
async def test_reconcile_with_no_sessions_returns_zero(
    test_session_factory,
) -> None:

    reconciled_count = await reconcile_orphaned_sessions(
        session_factory=test_session_factory,
    )

    assert reconciled_count == 0
