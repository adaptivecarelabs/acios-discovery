from acios_discovery.application.events.in_memory_event_publisher import (
    InMemoryEventPublisher,
)
from acios_discovery.application.subscribers.crawl_persistence_subscriber import (
    CrawlPersistenceSubscriber,
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


def test_persistence_subscriber_receives_events():

    publisher = InMemoryEventPublisher()

    subscriber = CrawlPersistenceSubscriber()

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

    assert len(
        subscriber.events,
    ) == 3

    assert isinstance(
        subscriber.events[0],
        JobCompletedEvent,
    )

    assert isinstance(
        subscriber.events[1],
        PageCrawledEvent,
    )

    assert isinstance(
        subscriber.events[2],
        CompanyDiscoveredEvent,
    )
