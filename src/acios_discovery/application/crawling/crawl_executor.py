from __future__ import annotations

from acios_discovery.application.crawling.crawl_execution_result import (
    CrawlExecutionResult,
)
from acios_discovery.application.crawling.crawl_worker import (
    CrawlWorker,
)
from acios_discovery.domain.queue.job_queue import (
    JobQueue,
)


class CrawlExecutor:
    """
    Consumes jobs from the queue until empty.
    """

    def __init__(
        self,
        *,
        queue: JobQueue,
        worker: CrawlWorker,
    ) -> None:

        self._queue = queue
        self._worker = worker

    async def execute(
        self,
    ) -> CrawlExecutionResult:

        result = CrawlExecutionResult()

        while True:

            job = await self._queue.dequeue()

            if job is None:
                break

            crawl_result = await self._worker.execute(
                job,
            )

            result.jobs_processed += 1

            result.pages_crawled += (
                crawl_result.pages_crawled
            )

            result.companies_discovered += (
                crawl_result.companies_discovered
            )

        return result
