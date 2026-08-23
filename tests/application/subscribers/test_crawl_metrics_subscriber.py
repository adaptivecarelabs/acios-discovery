import pytest

from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
)
from acios_discovery.application.subscribers.crawl_metrics_subscriber import (
    CrawlMetricsSubscriber,
)
from acios_discovery.domain.crawling import CrawlJob
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
from acios_discovery.domain.discovery.context import DiscoveryContext
from acios_discovery.domain.discovery.models import RawDiscovery
from acios_discovery.domain.discovery.record import DiscoveryRecord
from acios_discovery.domain.sources import Source


def make_job() -> CrawlJob:
    return CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.com/1",
        state="Lagos",
        city="Yaba",
        category_slug="restaurants",
    )


def make_record() -> DiscoveryRecord:
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
            business_name="Test Co",
        ),
    )


@pytest.mark.asyncio
async def test_subscriber_records_job_completed():
    metrics = CrawlMetricsService()
    subscriber = CrawlMetricsSubscriber(metrics=metrics)

    await subscriber(
        JobCompletedEvent(
            job=make_job(),
            pages_crawled=1,
            companies_discovered=2,
        )
    )

    assert metrics.snapshot().jobs_processed == 1


@pytest.mark.asyncio
async def test_subscriber_records_page_crawled():
    metrics = CrawlMetricsService()
    subscriber = CrawlMetricsSubscriber(metrics=metrics)

    await subscriber(
        PageCrawledEvent(
            job=make_job(),
            page_number=1,
            companies_found=2,
        )
    )

    assert metrics.snapshot().pages_crawled == 1


@pytest.mark.asyncio
async def test_subscriber_records_company_discovered():
    metrics = CrawlMetricsService()
    subscriber = CrawlMetricsSubscriber(metrics=metrics)

    await subscriber(
        CompanyDiscoveredEvent(
            record=make_record(),
        )
    )

    assert metrics.snapshot().companies_discovered == 1


@pytest.mark.asyncio
async def test_subscriber_records_job_retried():
    metrics = CrawlMetricsService()
    subscriber = CrawlMetricsSubscriber(metrics=metrics)

    await subscriber(
        JobRetriedEvent(
            job=make_job(),
            attempt=1,
            max_retries=3,
            error="simulated",
        )
    )

    assert metrics.snapshot().retries == 1


@pytest.mark.asyncio
async def test_subscriber_records_job_failed():
    metrics = CrawlMetricsService()
    subscriber = CrawlMetricsSubscriber(metrics=metrics)

    await subscriber(
        JobFailedEvent(
            job=make_job(),
            error="simulated",
            retryable=False,
        )
    )

    assert metrics.snapshot().failures == 1
