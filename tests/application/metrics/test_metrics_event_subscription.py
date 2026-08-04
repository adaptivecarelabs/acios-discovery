from acios_discovery.application.events.in_memory_event_publisher import (
    InMemoryEventPublisher,
)
from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
)
from acios_discovery.application.subscribers.crawl_metrics_subscriber import (
    CrawlMetricsSubscriber,
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


def test_metrics_are_updated_from_events():

    metrics = CrawlMetricsService()

    subscriber = CrawlMetricsSubscriber(
        metrics,
    )

    publisher = InMemoryEventPublisher()

    publisher.subscribe(
        subscriber,
    )

    publisher.publish(
        JobCompletedEvent(),
    )

    publisher.publish(
        PageCrawledEvent(),
    )

    publisher.publish(
        CompanyDiscoveredEvent(),
    )

    snapshot = metrics.snapshot()

    assert snapshot.jobs_processed == 1

    assert snapshot.pages_crawled == 1

    assert snapshot.companies_discovered == 1
