from __future__ import annotations

from collections.abc import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.application.persistence.crawl_session_persistence import (
    CrawlSessionPersistence,
)
from acios_discovery.domain.crawling.crawl_session import CrawlSession
from acios_discovery.infrastructure.persistence.repositories.crawl_session_repository import (
    SqlAlchemyCrawlSessionRepository,
)
from acios_discovery.application.persistence.crawl_job_persistence import (
    CrawlJobPersistence,
)
from acios_discovery.domain.crawling.job import CrawlJob
from acios_discovery.infrastructure.persistence.repositories.crawl_job_repository import (
    SqlAlchemyCrawlJobRepository,
)


class SessionScopedCrawlSessionPersistence(CrawlSessionPersistence):
    """
    Opens a fresh, short-lived AsyncSession for each save/load,
    commits, and closes it — matching the pattern the outbox
    relay entrypoint already uses. CrawlSupervisor may run for a
    long time; holding one session open for its entire lifetime
    would be unnecessary and risky.
    """

    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
    ) -> None:
        self._session_factory = session_factory

    async def save(
        self,
        session: CrawlSession,
    ) -> None:

        async with self._session_factory() as db_session:

            repository = SqlAlchemyCrawlSessionRepository(
                db_session,
            )

            await repository.save(
                session,
            )

            await db_session.commit()

    async def load(
        self,
        session_id: str,
    ) -> CrawlSession | None:

        async with self._session_factory() as db_session:

            repository = SqlAlchemyCrawlSessionRepository(
                db_session,
            )

            return await repository.get(
                session_id,
            )


class SessionScopedCrawlJobPersistence(CrawlJobPersistence):

    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
    ) -> None:
        self._session_factory = session_factory

    async def save(
        self,
        job: CrawlJob,
        *,
        session_id: str,
    ) -> None:

        async with self._session_factory() as db_session:

            repository = SqlAlchemyCrawlJobRepository(
                db_session,
            )

            await repository.save(
                job,
                session_id=session_id,
            )

            await db_session.commit()
