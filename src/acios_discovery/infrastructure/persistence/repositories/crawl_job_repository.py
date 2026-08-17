from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.domain.crawling.job import CrawlJob
from acios_discovery.domain.crawling.priority import CrawlPriority
from acios_discovery.domain.crawling.status import CrawlStatus
from acios_discovery.domain.repositories.crawl_job_repository import (
    CrawlJobRepository,
)
from acios_discovery.domain.sources.source import Source
from acios_discovery.infrastructure.persistence.orm.crawl_job import (
    CrawlJobORM,
)


class SqlAlchemyCrawlJobRepository(CrawlJobRepository):
    """
    SQLAlchemy repository for crawl jobs.

    session_id is persistence/application context and is therefore
    supplied separately from the CrawlJob domain object.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def save(
        self,
        job: CrawlJob,
        *,
        session_id: str,
    ) -> None:
        orm = await self._session.get(
            CrawlJobORM,
            job.id,
        )

        now = datetime.now(UTC)

        if orm is None:
            orm = CrawlJobORM(
                id=job.id,
                session_id=session_id,
                source=str(job.source),
                listing_url=job.listing_url,
                state=job.state,
                city=job.city,
                category_slug=job.category_slug,
                page=job.page,
                priority=int(job.priority),
                retries=job.retries,
                max_retries=job.max_retries,
                status=str(job.status),
                created_at=now,
                updated_at=now,
            )

            self._session.add(orm)
            return

        orm.session_id = session_id
        orm.source = str(job.source)
        orm.listing_url = job.listing_url
        orm.state = job.state
        orm.city = job.city
        orm.category_slug = job.category_slug
        orm.page = job.page
        orm.priority = int(job.priority)
        orm.retries = job.retries
        orm.max_retries = job.max_retries
        orm.status = str(job.status)
        orm.updated_at = now

    async def get(
        self,
        job_id: str,
    ) -> CrawlJob | None:
        stmt = (
            select(CrawlJobORM)
            .where(
                CrawlJobORM.id == job_id,
            )
        )

        result = await self._session.execute(stmt)

        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return CrawlJob(
            id=orm.id,
            source=Source(orm.source),
            listing_url=orm.listing_url,
            state=orm.state,
            city=orm.city,
            category_slug=orm.category_slug,
            page=orm.page,
            priority=CrawlPriority(orm.priority),
            retries=orm.retries,
            max_retries=orm.max_retries,
            status=CrawlStatus(orm.status),
        )

    async def list_by_session(
        self,
        session_id: str,
    ) -> list[CrawlJob]:
        stmt = (
            select(CrawlJobORM)
            .where(
                CrawlJobORM.session_id == session_id,
            )
            .order_by(
                CrawlJobORM.priority,
                CrawlJobORM.created_at,
            )
        )

        result = await self._session.execute(stmt)

        rows = result.scalars().all()

        return [
            CrawlJob(
                id=row.id,
                source=Source(row.source),
                listing_url=row.listing_url,
                state=row.state,
                city=row.city,
                category_slug=row.category_slug,
                page=row.page,
                priority=CrawlPriority(row.priority),
                retries=row.retries,
                max_retries=row.max_retries,
                status=CrawlStatus(row.status),
            )
            for row in rows
        ]

    async def delete(
        self,
        job_id: str,
    ) -> None:
        stmt = (
            delete(CrawlJobORM)
            .where(
                CrawlJobORM.id == job_id,
            )
        )

        await self._session.execute(stmt)
