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
from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.discovery.context import DiscoveryContext
from acios_discovery.domain.discovery.models import RawDiscovery
from acios_discovery.domain.discovery.record import DiscoveryRecord
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
from acios_discovery.domain.errors.crawl_errors import (
    FatalCrawlError,
    RetryableCrawlError,
)
from acios_discovery.domain.events.job_failed_event import JobFailedEvent
from acios_discovery.domain.events.job_retried_event import JobRetriedEvent




def make_record(name: str) -> DiscoveryRecord:
    return DiscoveryRecord(
        context=DiscoveryContext(
            source=Source.FINELIB,
            state="Lagos",
            city="Yaba",
            category="restaurants",
            listing_url="https://example.com",
        ),
        company=RawDiscovery(
            source=Source.FINELIB,
            business_name=name,
        ),
    )


class FakeWorker:
    async def execute(self, job):
        return ListingCrawlResult(
            pages_crawled=1,
            companies_discovered=2,
            records=[
                make_record("Company A"),
                make_record("Company B"),
            ],
        )


class EventRecorder:
    def __init__(self):
        self.events = []

    async def __call__(self, event):
        self.events.append(event)


class PartiallyFailingWorker:
    async def execute(self, job):
        if job.listing_url.endswith("/2"):
            raise RuntimeError("crawl failed")

        return ListingCrawlResult(
            pages_crawled=1,
            companies_discovered=2,
            records=[],
        )


    
class AlwaysRetryableWorker:
    """Fails every attempt with a RetryableCrawlError."""

    def __init__(self) -> None:
        self.attempts = 0

    async def execute(self, job):
        self.attempts += 1
        raise RetryableCrawlError("simulated transient failure")


class SucceedsOnThirdAttemptWorker:
    """Fails twice with a retryable error, succeeds on the 3rd try."""

    def __init__(self) -> None:
        self.attempts = 0

    async def execute(self, job):
        self.attempts += 1

        if self.attempts < 3:
            raise RetryableCrawlError("simulated transient failure")

        return ListingCrawlResult(
            pages_crawled=1,
            companies_discovered=1,
            records=[],
        )

class FatalWorker:
    async def execute(self, job):
        raise FatalCrawlError("simulated fatal failure")


@pytest.mark.asyncio
async def test_pool_processes_jobs():
    queue = InMemoryJobQueue()
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
        publisher=publisher,
        workers=4,
    )

    result = await pool.execute()

    assert result.completed is True
    assert result.workers == 4
    assert result.jobs_processed == 10
    assert result.pages_crawled == 10
    assert result.companies_discovered == 20
    assert result.jobs_failed == 0


@pytest.mark.asyncio
async def test_pool_publishes_events():
    queue = InMemoryJobQueue()

    publisher = InMemoryEventPublisher()

    recorder = EventRecorder()

    publisher.subscribe(
        recorder,
    )


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
        publisher=publisher,
        workers=4,
    )

    await pool.execute()

    job_events = [
        event
        for event in recorder.events
        if isinstance(
            event,
            JobCompletedEvent,
        )
    ]

    page_events = [
        event
        for event in recorder.events
        if isinstance(
            event,
            PageCrawledEvent,
        )
    ]

    company_events = [
        event
        for event in recorder.events
        if isinstance(
            event,
            CompanyDiscoveredEvent,
        )
    ]

    assert len(job_events) == 10

    assert all(
        isinstance(
            event,
            JobCompletedEvent,
        )
        for event in job_events
    )

    assert len(page_events) == 10

    assert all(
        isinstance(
            event,
            PageCrawledEvent,
        )
        for event in page_events
    )

    for event in page_events:
        assert event.job.source is Source.FINELIB
        assert event.job.state == "Lagos"
        assert event.job.city == "Yaba"
        assert event.job.category_slug == "restaurants"
        assert event.page_number == 1
        assert event.companies_found == 2

    assert len(company_events) == 20

    assert all(
        isinstance(
            event,
            CompanyDiscoveredEvent,
        )
        for event in company_events
    )



@pytest.mark.asyncio
async def test_pool_records_failed_jobs_and_continues() -> None:
    queue = InMemoryJobQueue()
    publisher = InMemoryEventPublisher()

    for i in range(5):
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
        worker_factory=lambda: PartiallyFailingWorker(),
        publisher=publisher,
        workers=2,
    )

    result = await pool.execute()

    assert result.completed is True
    assert result.jobs_processed == 4
    assert result.jobs_failed == 1
    assert result.pages_crawled == 4
    assert result.companies_discovered == 8


@pytest.mark.asyncio
async def test_pool_completes_when_queue_is_empty() -> None:
    queue = InMemoryJobQueue()
    publisher = InMemoryEventPublisher()

    pool = ConcurrentWorkerPool(
        queue=queue,
        worker_factory=lambda: FakeWorker(),
        publisher=publisher,
        workers=4,
    )

    result = await pool.execute()

    assert result.completed is True
    assert result.workers == 4
    assert result.jobs_processed == 0
    assert result.jobs_failed == 0
    assert result.pages_crawled == 0
    assert result.companies_discovered == 0


@pytest.mark.asyncio
async def test_retryable_error_retries_in_place_up_to_max_retries():
    queue = InMemoryJobQueue()
    publisher = InMemoryEventPublisher()
    recorder = EventRecorder()
    publisher.subscribe(recorder)

    await queue.enqueue(
        CrawlJob(
            source=Source.FINELIB,
            listing_url="https://example.com/1",
            state="Lagos",
            city="Yaba",
            category_slug="restaurants",
            max_retries=2,
        )
    )

    worker = AlwaysRetryableWorker()

    pool = ConcurrentWorkerPool(
        queue=queue,
        worker_factory=lambda: worker,
        publisher=publisher,
        workers=1,
        session_id="test-session",
    )

    result = await pool.execute()

    # 1 initial attempt + 2 retries = 3 total attempts, same job,
    # never re-enqueued.
    assert worker.attempts == 3

    assert result.jobs_processed == 0
    assert result.jobs_failed == 1

    retried_events = [
        event for event in recorder.events
        if isinstance(event, JobRetriedEvent)
    ]
    failed_events = [
        event for event in recorder.events
        if isinstance(event, JobFailedEvent)
    ]

    assert len(retried_events) == 2
    assert [event.attempt for event in retried_events] == [1, 2]

    assert len(failed_events) == 1
    assert failed_events[0].retryable is True


@pytest.mark.asyncio
async def test_retryable_error_succeeds_within_retry_budget():
    queue = InMemoryJobQueue()
    publisher = InMemoryEventPublisher()
    recorder = EventRecorder()
    publisher.subscribe(recorder)

    await queue.enqueue(
        CrawlJob(
            source=Source.FINELIB,
            listing_url="https://example.com/1",
            state="Lagos",
            city="Yaba",
            category_slug="restaurants",
            max_retries=3,
        )
    )

    worker = SucceedsOnThirdAttemptWorker()

    pool = ConcurrentWorkerPool(
        queue=queue,
        worker_factory=lambda: worker,
        publisher=publisher,
        workers=1,
    )

    result = await pool.execute()

    assert worker.attempts == 3
    assert result.jobs_processed == 1
    assert result.jobs_failed == 0

    completed_events = [
        event for event in recorder.events
        if isinstance(event, JobCompletedEvent)
    ]
    retried_events = [
        event for event in recorder.events
        if isinstance(event, JobRetriedEvent)
    ]
    failed_events = [
        event for event in recorder.events
        if isinstance(event, JobFailedEvent)
    ]

    assert len(completed_events) == 1
    assert len(retried_events) == 2
    assert len(failed_events) == 0


@pytest.mark.asyncio
async def test_fatal_error_fails_immediately_without_retry():
    queue = InMemoryJobQueue()
    publisher = InMemoryEventPublisher()
    recorder = EventRecorder()
    publisher.subscribe(recorder)

    await queue.enqueue(
        CrawlJob(
            source=Source.FINELIB,
            listing_url="https://example.com/1",
            state="Lagos",
            city="Yaba",
            category_slug="restaurants",
            max_retries=5,
        )
    )

    worker = FatalWorker()

    pool = ConcurrentWorkerPool(
        queue=queue,
        worker_factory=lambda: worker,
        publisher=publisher,
        workers=1,
    )

    result = await pool.execute()

    assert result.jobs_failed == 1

    retried_events = [
        event for event in recorder.events
        if isinstance(event, JobRetriedEvent)
    ]
    failed_events = [
        event for event in recorder.events
        if isinstance(event, JobFailedEvent)
    ]

    # A FatalCrawlError (or any non-RetryableCrawlError) never
    # retries, even with a generous max_retries budget.
    assert len(retried_events) == 0
    assert len(failed_events) == 1
    assert failed_events[0].retryable is False
