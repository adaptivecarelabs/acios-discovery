from __future__ import annotations

import asyncio

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
from acios_discovery.application.persistence.crawl_job_persistence import (
    CrawlJobPersistence,
)
from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.crawling.status import CrawlStatus
from acios_discovery.domain.errors.crawl_errors import RetryableCrawlError
from acios_discovery.domain.events.company_discovered_event import (
    CompanyDiscoveredEvent,
)
from acios_discovery.domain.events.job_completed_event import (
    JobCompletedEvent,
)
from acios_discovery.domain.events.job_failed_event import JobFailedEvent
from acios_discovery.domain.events.job_retried_event import JobRetriedEvent
from acios_discovery.domain.events.page_crawled_event import (
    PageCrawledEvent,
)
from acios_discovery.domain.queue.job_queue import JobQueue
from acios_discovery.shared.logging import logger


class ConcurrentWorkerPool:
    """
    Executes multiple crawl workers concurrently.

    Every worker consumes jobs from the same queue until
    the queue becomes empty.

    A job that fails with a RetryableCrawlError is retried in
    place (same worker, same job) up to job.max_retries times —
    NOT re-enqueued, because InMemoryJobQueue.dequeue() returns
    None permanently once empty and every worker exits on that;
    a retried job re-entering the queue after other workers have
    already exited could be stranded with no consumer left.

    Any other exception (including FatalCrawlError) fails the job
    immediately with no retry. A failure in one job is recorded
    and does not terminate the worker — it continues consuming
    subsequent jobs from the queue.
    """

    def __init__(
        self,
        *,
        queue: JobQueue,
        worker_factory: CrawlWorkerFactory,
        publisher: InMemoryEventPublisher,
        workers: int = 4,
        session_id: str | None = None,
        job_persistence: CrawlJobPersistence | None = None,
    ) -> None:
        if workers < 1:
            raise ValueError(
                "workers must be greater than zero",
            )

        self._queue = queue
        self._worker_factory = worker_factory
        self._publisher = publisher
        self._workers = workers
        self._session_id = session_id or "unknown"
        self._job_persistence=job_persistence


    async def _persist_job(self, job: CrawlJob) -> None:
        if self._job_persistence is None:
            return
    
        await self._job_persistence.save(
            job,
            session_id=self._session_id,
        )

    async def execute(self) -> WorkerPoolResult:
        result = WorkerPoolResult(
            workers=self._workers,
            completed=False,
        )

        lock = asyncio.Lock()

        async def run_job(
            worker: CrawlWorker,
            job: CrawlJob,
        ) -> None:

            attempt = 0

            job.status = CrawlStatus.RUNNING
            await self._persist_job(job)

            while True:

                try:
                    crawl_result: ListingCrawlResult = (
                        await worker.execute(job)
                    )

                except RetryableCrawlError as exc:

                    attempt += 1

                    if attempt <= job.max_retries:

                        logger.warning(
                            "Retryable error (session=%s job=%s "
                            "city=%s category=%s page=%s) "
                            "attempt %s/%s: %s",
                            self._session_id,
                            job.id,
                            job.city,
                            job.category_slug,
                            job.page,
                            attempt,
                            job.max_retries,
                            exc,
                        )

                        job.retries = attempt
                        job.status = CrawlStatus.RETRYING

                        await self._persist_job(job)

                        await self._publisher.publish(
                            JobRetriedEvent(
                                job=job,
                                attempt=attempt,
                                max_retries=job.max_retries,
                                error=str(exc),
                            )
                        )

                        job.status = CrawlStatus.RUNNING
                        continue

                    logger.error(
                        "Job exhausted retries (session=%s job=%s "
                        "city=%s category=%s page=%s) after %s "
                        "attempts: %s",
                        self._session_id,
                        job.id,
                        job.city,
                        job.category_slug,
                        job.page,
                        job.max_retries,
                        exc,
                    )

                    job.status = CrawlStatus.FAILED

                    await self._persist_job(job)

                    async with lock:
                        result.jobs_failed += 1

                    await self._publisher.publish(
                        JobFailedEvent(
                            job=job,
                            error=str(exc),
                            retryable=True,
                        )
                    )

                    return

                except Exception as exc:

                    logger.error(
                        "Fatal error (session=%s job=%s city=%s "
                        "category=%s page=%s): %s",
                        self._session_id,
                        job.id,
                        job.city,
                        job.category_slug,
                        job.page,
                        exc,
                        exc_info=True,
                    )

                    job.status = CrawlStatus.FAILED

                    await self._persist_job(job)

                    async with lock:
                        result.jobs_failed += 1

                    await self._publisher.publish(
                        JobFailedEvent(
                            job=job,
                            error=str(exc),
                            retryable=False,
                        )
                    )

                    return

                job.status = CrawlStatus.COMPLETED

                await self._persist_job(job)

                async with lock:
                    result.jobs_processed += 1
                    result.pages_crawled += (
                        crawl_result.pages_crawled
                    )
                    result.companies_discovered += (
                        crawl_result.companies_discovered
                    )
                    result.enrichment_failures += (
                        len(crawl_result.errors)
                    )

                await self._publish_crawl_events(
                    job=job,
                    crawl_result=crawl_result,
                )

                return

        async def run_worker() -> None:
            worker: CrawlWorker = self._worker_factory()

            while True:
                job = await self._queue.dequeue()

                if job is None:
                    break

                await run_job(worker, job)

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
