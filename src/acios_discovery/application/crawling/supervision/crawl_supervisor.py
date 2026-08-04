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

        worker_result = await self._worker_pool.execute()

        snapshot = self._metrics.runtime_snapshot(
            workers=worker_result.workers,
        )

        return CrawlSupervisorResult(
            session_id=self._session.id,
            workers=snapshot.workers,
            jobs_processed=snapshot.jobs_processed,
            pages_crawled=snapshot.pages_crawled,
            companies_discovered=snapshot.companies_discovered,
        )
