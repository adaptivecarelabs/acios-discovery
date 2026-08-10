from __future__ import annotations

from acios_discovery.application.crawling.supervision.crawl_supervisor_result import (
    CrawlSupervisorResult,
)
from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
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
        metrics: CrawlMetricsService,
    ) -> None:
        self._session = session
        self._worker_pool = worker_pool
        self._metrics = metrics

    async def run(
        self,
    ) -> CrawlSupervisorResult:

        self._session.start()

        try:
            worker_result = await self._worker_pool.execute()

            self._session.jobs_completed = (
                worker_result.jobs_processed
            )

            self._session.jobs_failed = (
                worker_result.jobs_failed
            )

            self._session.pages_crawled = (
                worker_result.pages_crawled
            )

            self._session.companies_discovered = (
                worker_result.companies_discovered
            )

            if worker_result.completed:
                self._session.complete()
            else:
                self._session.fail()

            return CrawlSupervisorResult(
                session_id=self._session.id,
                workers=worker_result.workers,
                jobs_processed=worker_result.jobs_processed,
                pages_crawled=worker_result.pages_crawled,
                companies_discovered=(
                    worker_result.companies_discovered
                ),
            )

        except Exception:
            self._session.fail()
            raise
