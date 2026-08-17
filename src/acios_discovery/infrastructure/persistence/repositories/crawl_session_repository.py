from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.domain.crawling.crawl_session import (
    CrawlSession,
)
from acios_discovery.domain.crawling.crawl_session_status import (
    CrawlSessionStatus,
)
from acios_discovery.domain.repositories.crawl_session_repository import (
    CrawlSessionRepository,
)
from acios_discovery.infrastructure.persistence.orm.crawl_session import (
    CrawlSessionORM,
)


class SqlAlchemyCrawlSessionRepository(CrawlSessionRepository):
    """
    SQLAlchemy repository for crawl sessions.

    The repository operates on an externally supplied AsyncSession
    so it participates in the UnitOfWork transaction.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def save(
        self,
        session: CrawlSession,
    ) -> None:
        orm = await self._session.get(
            CrawlSessionORM,
            session.id,
        )

        now = datetime.now(UTC)

        if orm is None:
            orm = CrawlSessionORM(
                id=session.id,
                status=str(session.status),
                started_at=session.started_at,
                finished_at=session.finished_at,
                jobs_total=session.jobs_total,
                jobs_completed=session.jobs_completed,
                jobs_failed=session.jobs_failed,
                retries=session.retries,
                pages_crawled=session.pages_crawled,
                companies_discovered=session.companies_discovered,
                created_at=now,
                updated_at=now,
            )

            self._session.add(orm)
            return

        orm.status = str(session.status)
        orm.started_at = session.started_at
        orm.finished_at = session.finished_at
        orm.jobs_total = session.jobs_total
        orm.jobs_completed = session.jobs_completed
        orm.jobs_failed = session.jobs_failed
        orm.retries = session.retries
        orm.pages_crawled = session.pages_crawled
        orm.companies_discovered = session.companies_discovered
        orm.updated_at = now

    async def get(
        self,
        session_id: str,
    ) -> CrawlSession | None:
        stmt = (
            select(CrawlSessionORM)
            .where(
                CrawlSessionORM.id == session_id,
            )
        )

        result = await self._session.execute(stmt)

        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return CrawlSession(
            id=orm.id,
            status=CrawlSessionStatus(orm.status),
            started_at=orm.started_at,
            finished_at=orm.finished_at,
            jobs_total=orm.jobs_total,
            jobs_completed=orm.jobs_completed,
            jobs_failed=orm.jobs_failed,
            retries=orm.retries,
            pages_crawled=orm.pages_crawled,
            companies_discovered=orm.companies_discovered,
        )

    async def list_all(
        self,
    ) -> list[CrawlSession]:
        stmt = (
            select(CrawlSessionORM)
            .order_by(
                CrawlSessionORM.created_at,
            )
        )

        result = await self._session.execute(stmt)

        rows = result.scalars().all()

        return [
            CrawlSession(
                id=row.id,
                status=CrawlSessionStatus(row.status),
                started_at=row.started_at,
                finished_at=row.finished_at,
                jobs_total=row.jobs_total,
                jobs_completed=row.jobs_completed,
                jobs_failed=row.jobs_failed,
                retries=row.retries,
                pages_crawled=row.pages_crawled,
                companies_discovered=row.companies_discovered,
            )
            for row in rows
        ]

    async def delete(
        self,
        session_id: str,
    ) -> None:
        stmt = (
            delete(CrawlSessionORM)
            .where(
                CrawlSessionORM.id == session_id,
            )
        )

        await self._session.execute(stmt)
