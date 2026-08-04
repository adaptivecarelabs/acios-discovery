from __future__ import annotations

import asyncio

from acios_discovery.application.crawling.worker_pool_result import (
    WorkerPoolResult,
)
from acios_discovery.application.events.in_memory_event_publisher import (
    InMemoryEventPublisher,
)
from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
)
from acios_discovery.domain.events.company_discovered_event import (
    CompanyDiscoveredEvent,
)
from acios_discovery.domain.events.job_completed_event import (
    JobCompletedEvent,
)
from acios_discovery.domain.events.page_crawled_event import (
    PageCrawledEvent,
)
from acios_discovery.domain.queue.job_queue import (
    JobQueue,
)


class ConcurrentWorkerPool:
    """
    Executes multiple crawl workers concurrently.

    Every worker consumes from the same queue until
    the queue becomes empty.
    """

    def __init__(
        self,
        *,
        queue: JobQueue,
        worker_factory,
        metrics: CrawlMetricsService,
        publisher: InMemoryEventPublisher,
        workers: int = 4,
    ) -> None:

        self._queue = queue
        self._worker_factory = worker_factory
        self._metrics = metrics
        self._publisher = publisher
        self._workers = workers

    async def execute(
        self,
    ) -> WorkerPoolResult:

        result = WorkerPoolResult(
            workers=self._workers,
            completed=False,
        )

        lock = asyncio.Lock()

        async def run_worker() -> None:

            worker = self._worker_factory()

            while True:

                job = await self._queue.dequeue()

                if job is None:
                    break

                crawl_result = await worker.execute(
                    job,
                )

                async with lock:

                    self._publisher.publish(
                        JobCompletedEvent(),
                    )

                    for _ in range(crawl_result.pages_crawled):
                        self._publisher.publish(
                            PageCrawledEvent(),
                        )

                    for _ in range(
                        crawl_result.companies_discovered
                    ):
                        self._publisher.publish(
                            CompanyDiscoveredEvent(),
                        )

        await asyncio.gather(
            *[
                run_worker()
                for _ in range(
                    self._workers,
                )
            ]
        )

        result.completed = True
        return result
