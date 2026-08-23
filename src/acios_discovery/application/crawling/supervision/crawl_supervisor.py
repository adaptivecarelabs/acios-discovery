from __future__ import annotations
from acios_discovery.shared.logging import logger
from acios_discovery.application.crawling.supervision.crawl_supervisor_result import (
    CrawlSupervisorResult,
)
from acios_discovery.application.persistence.crawl_session_persistence import (
    CrawlSessionPersistence,
)


class CrawlSupervisor:
    """
    Coordinates the execution of an entire
    crawl session.
    """

    def __init__(
        self,
        *,
        session,
        worker_pool,
        session_persistence: CrawlSessionPersistence | None = None,
        resumed: bool = False,
    ) -> None:
        self._session = session
        self._worker_pool = worker_pool
        self._session_persistence = session_persistence
        self._resumed = resumed

    async def _persist(self) -> None:

        if self._session_persistence is None:
            return

        await self._session_persistence.save(
            self._session,
        )

    async def _load_prior_progress(self) -> None:
        """
        On resume, load this session's previously persisted
        progress so the new run's results accumulate onto it
        instead of overwriting it.
        """

        if self._session_persistence is None:
            return

        existing = await self._session_persistence.load(
            self._session.id,
        )

        if existing is None:
            return

        self._session.jobs_completed = existing.jobs_completed
        self._session.jobs_failed = existing.jobs_failed
        self._session.retries = existing.retries
        self._session.pages_crawled = existing.pages_crawled
        self._session.companies_discovered = (
            existing.companies_discovered
        )

    async def run(
        self,
    ) -> CrawlSupervisorResult:

        if self._resumed:
            await self._load_prior_progress()

        self._session.start()

        await self._persist()

        try:
            worker_result = await self._worker_pool.execute()

            #
            # Additive, not assignment: on a fresh run the prior
            # values are 0, so this is equivalent to the old
            # behavior; on resume, it correctly accumulates onto
            # progress loaded above.
            #

            self._session.jobs_completed += (
                worker_result.jobs_processed
            )

            self._session.jobs_failed += (
                worker_result.jobs_failed
            )

            self._session.pages_crawled += (
                worker_result.pages_crawled
            )

            self._session.companies_discovered += (
                worker_result.companies_discovered
            )

            if worker_result.completed:
                self._session.complete()
            else:
                self._session.fail()

            await self._persist()

            return CrawlSupervisorResult(
                session_id=self._session.id,
                workers=worker_result.workers,
                jobs_processed=worker_result.jobs_processed,
                jobs_failed=worker_result.jobs_failed,
                pages_crawled=worker_result.pages_crawled,
                companies_discovered=(
                    worker_result.companies_discovered
                ),
            )

        except Exception as exc:

            logger.error(
                "Crawl session failed catastrophically "
                "(session=%s): %s",
                self._session.id,
                exc,
                exc_info=True,
            )

            self._session.fail()
            await self._persist()
            raise
