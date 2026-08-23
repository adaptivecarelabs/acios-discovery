from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.application.persistence.crawl_job_persistence import (
    CrawlJobPersistence,
)
from acios_discovery.domain.crawling.job import CrawlJob
from acios_discovery.domain.crawling.status import CrawlStatus
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.persistence.orm.crawl_job import (
    CrawlJobORM,
)
from acios_discovery.infrastructure.persistence.orm.crawl_session import (
    CrawlSessionORM,
)
from acios_discovery.infrastructure.persistence.session_scoped_crawl_persistence import (
    SessionScopedCrawlJobPersistence,
)


@pytest.mark.asyncio
async def test_job_persistence_writes_and_updates_status(
    db_session: AsyncSession,
    test_session_factory,
) -> None:

    now = datetime.now(UTC)

    # A CrawlJobORM row has a FK to crawl_sessions, so a session
    # row must exist first.
    session_row = CrawlSessionORM(
        id="job-persistence-test-session",
        status="running",
        jobs_total=0,
        jobs_completed=0,
        jobs_failed=0,
        retries=0,
        pages_crawled=0,
        companies_discovered=0,
        created_at=now,
        updated_at=now,
    )
    db_session.add(session_row)
    await db_session.commit()

    persistence: CrawlJobPersistence = SessionScopedCrawlJobPersistence(
        test_session_factory,
    )

    job = CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.test/job-persistence",
        state="Lagos",
        city="Yaba",
        category_slug="restaurants",
    )

    job.status = CrawlStatus.RUNNING

    await persistence.save(
        job,
        session_id=session_row.id,
    )

    row = (
        await db_session.execute(
            select(CrawlJobORM).where(CrawlJobORM.id == job.id)
        )
    ).scalar_one()

    assert row.status == "running"
    assert row.city == "Yaba"

    job.status = CrawlStatus.COMPLETED

    await persistence.save(
        job,
        session_id=session_row.id,
    )

    db_session.expire_all()

    updated_row = (
        await db_session.execute(
            select(CrawlJobORM).where(CrawlJobORM.id == job.id)
        )
    ).scalar_one()

    assert updated_row.status == "completed"
