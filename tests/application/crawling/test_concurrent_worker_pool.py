import pytest

from acios_discovery.application.crawling.concurrent_worker_pool import (
    ConcurrentWorkerPool,
)
from acios_discovery.application.discovery.listing_crawl_result import (
    ListingCrawlResult,
)
from acios_discovery.application.events.in_memory_event_publisher import (
    InMemoryEventPublisher,
)
from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
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
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.queue.in_memory_job_queue import (
    InMemoryJobQueue,
)


class FakeWorker:

    async def execute(self, job):

        return ListingCrawlResult(
            pages_crawled=1,
            companies_discovered=2,
        )


class EventRecorder:

    def __init__(self):

        self.events = []

    def __call__(self, event):

        self.events.append(event)



@pytest.mark.asyncio
async def test_pool_processes_jobs():

    queue = InMemoryJobQueue()
    metrics = CrawlMetricsService()
    publisher = InMemoryEventPublisher()

    for i in range(10):

        await queue.enqueue(
            CrawlJob(
                source=Source.FINELIB,
                listing_url=f"https://example.com/{i}",
                state="Lagos",
                city="Yaba",
                category_slug="restaurants",
            )
        )

    pool = ConcurrentWorkerPool(
        queue=queue,
        worker_factory=lambda: FakeWorker(),
        metrics=metrics,
        publisher=publisher,
        workers=4,
    )

    result = await pool.execute()


    assert result.completed is True

    assert result.workers == 4


@pytest.mark.asyncio
async def test_pool_publishes_events():

    queue = InMemoryJobQueue()

    publisher = InMemoryEventPublisher()

    recorder = EventRecorder()

    publisher.subscribe(
        recorder,
    )

    metrics = CrawlMetricsService()

    for i in range(10):

        await queue.enqueue(
            CrawlJob(
                source=Source.FINELIB,
                listing_url=f"https://example.com/{i}",
                state="Lagos",
                city="Yaba",
                category_slug="restaurants",
            )
        )

    pool = ConcurrentWorkerPool(
        queue=queue,
        worker_factory=lambda: FakeWorker(),
        metrics=metrics,
        publisher=publisher,
        workers=4,
    )

    await pool.execute()

    job_events = [
        e
        for e in recorder.events
        if isinstance(
            e,
            JobCompletedEvent,
        )
    ]

    page_events = [
        e
        for e in recorder.events
        if isinstance(
            e,
            PageCrawledEvent,
        )
    ]

    company_events = [
        e
        for e in recorder.events
        if isinstance(
            e,
            CompanyDiscoveredEvent,
        )
    ]

    assert len(job_events) == 10

    assert all(
        isinstance(event, JobCompletedEvent)
        for event in job_events
    )

    assert len(page_events) == 10

    assert all(
        isinstance(event, PageCrawledEvent)
        for event in page_events
    )

    assert len(company_events) == 20

    assert all(
        isinstance(event, CompanyDiscoveredEvent)
        for event in company_events
    )
