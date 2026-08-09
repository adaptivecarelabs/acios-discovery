from __future__ import annotations

from acios_discovery.application.crawling.crawl_execution_result import (
    CrawlExecutionResult,
)
from acios_discovery.application.discovery.listing_crawl_result import (
    ListingCrawlResult,
)
from acios_discovery.domain.queue.job_queue import JobQueue


class CrawlExecutor:
    """
    Consumes crawl jobs from the queue until the queue is empty.
    """

    def __init__(
        self,
        *,
        queue: JobQueue,
        worker,
    ) -> None:
        self._queue = queue
        self._worker = worker

    async def execute(self) -> CrawlExecutionResult:
        result = CrawlExecutionResult()

        while True:
            job = await self._queue.dequeue()

            if job is None:
                break

            try:
                crawl_result: ListingCrawlResult = (
                    await self._worker.execute(job)
                )

                result.jobs_processed += 1

                result.pages_crawled += (
                    crawl_result.pages_crawled
                )

                result.companies_discovered += (
                    crawl_result.companies_discovered
                )

            except Exception:
                result.jobs_failed += 1

        return result
