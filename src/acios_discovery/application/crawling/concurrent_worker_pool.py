from __future__ import annotations

import asyncio
import traceback

from acios_discovery.application.crawling.crawl_worker import (
    CrawlWorker,
)
from acios_discovery.application.crawling.crawl_worker_factory import (
    CrawlWorkerFactory,
)
from acios_discovery.application.crawling.worker_pool_result import (
    WorkerPoolResult,
)
from acios_discovery.application.discovery.listing_crawl_result import (
    ListingCrawlResult,
)
from acios_discovery.application.events.in_memory_event_publisher import (
    InMemoryEventPublisher,
)
from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.events.company_discovered_event import (
    CompanyDiscoveredEvent,
)
from acios_discovery.domain.events.job_completed_event import (
    JobCompletedEvent,
)
from acios_discovery.domain.events.page_crawled_event import (
    PageCrawledEvent,
)
from acios_discovery.domain.queue.job_queue import JobQueue


class ConcurrentWorkerPool:
    """
    Executes multiple crawl workers concurrently.

    Every worker consumes jobs from the same queue until
    the queue becomes empty.

    A failure in one crawl job is recorded and does not
    terminate the worker. The worker continues consuming
    subsequent jobs from the queue.
    """

    def __init__(
        self,
        *,
        queue: JobQueue,
        worker_factory: CrawlWorkerFactory,
        publisher: InMemoryEventPublisher,
        workers: int = 4,
    ) -> None:
        if workers < 1:
            raise ValueError(
                "workers must be greater than zero",
            )

        self._queue = queue
        self._worker_factory = worker_factory
        self._publisher = publisher
        self._workers = workers

    async def execute(self) -> WorkerPoolResult:
        result = WorkerPoolResult(
            workers=self._workers,
            completed=False,
        )

        lock = asyncio.Lock()

        async def run_worker() -> None:
            worker: CrawlWorker = self._worker_factory()

            while True:
                job = await self._queue.dequeue()

                if job is None:
                    break

                try:
                    crawl_result: ListingCrawlResult = (
                        await worker.execute(job)
                    )

                    async with lock:
                        result.jobs_processed += 1
                        result.pages_crawled += (
                            crawl_result.pages_crawled
                        )
                        result.companies_discovered += (
                            crawl_result.companies_discovered
                        )

                    await self._publish_crawl_events(
                        job=job,
                        crawl_result=crawl_result,
                    )

                except Exception:
                    async with lock:
                        result.jobs_failed += 1

                    traceback.print_exc()

                    # A failed job must not kill the worker.
                    # Continue consuming the remaining queue.
                    continue

        await asyncio.gather(
            *[
                run_worker()
                for _ in range(self._workers)
            ]
        )

        result.completed = True

        return result

    async def _publish_crawl_events(
        self,
        *,
        job: CrawlJob,
        crawl_result: ListingCrawlResult,
    ) -> None:
        await self._publisher.publish(
            JobCompletedEvent(
                job=job,
                pages_crawled=crawl_result.pages_crawled,
                companies_discovered=(
                    crawl_result.companies_discovered
                ),
            )
        )

        for page_number in range(
            1,
            crawl_result.pages_crawled + 1,
        ):
            await self._publisher.publish(
                PageCrawledEvent(
                    job=job,
                    page_number=page_number,
                    companies_found=(
                        crawl_result.companies_discovered
                    ),
                )
            )

        for record in crawl_result.records:
            await self._publisher.publish(
                CompanyDiscoveredEvent(
                    record=record,
                )
            )
