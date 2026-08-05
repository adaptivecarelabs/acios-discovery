from acios_discovery.application.events.in_memory_event_publisher import (
    InMemoryEventPublisher,
)
from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
)
from acios_discovery.application.subscribers.crawl_metrics_subscriber import (
    CrawlMetricsSubscriber,
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


def make_record() -> DiscoveryRecord:
    return DiscoveryRecord(
        context=DiscoveryContext(
            source="Finelib",
            state="Lagos",
            city="Yaba",
            category="restaurants",
            listing_url="https://example.com",
        ),
        company=RawDiscovery(
            source="Finelib",
            business_name="ABC Ltd",
        ),
    )




async def test_metrics_are_updated_from_events():

    job = CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.com",
        state="Lagos",
        city="Yaba",
        category_slug="restaurants",
    )

    metrics = CrawlMetricsService()

    subscriber = CrawlMetricsSubscriber(
        metrics,
    )

    publisher = InMemoryEventPublisher()

    publisher.subscribe(
        subscriber,
    )

    await publisher.publish(
        JobCompletedEvent(
            job=job,
            pages_crawled=1,
            companies_discovered=2,
        )
    )

    await publisher.publish(
        PageCrawledEvent(
            job=job,
            page_number=1,
            companies_found=2,
        )
    )

    await publisher.publish(
        CompanyDiscoveredEvent(
            record=make_record(),
        )
    )

    snapshot = metrics.snapshot()

    assert snapshot.jobs_processed == 1

    assert snapshot.pages_crawled == 1

    assert snapshot.companies_discovered == 1
