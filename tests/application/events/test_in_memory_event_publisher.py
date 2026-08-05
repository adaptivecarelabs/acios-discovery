from acios_discovery.application.events.in_memory_event_publisher import (
    InMemoryEventPublisher,
)
from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.events.page_crawled_event import (
    PageCrawledEvent,
)
from acios_discovery.domain.sources import Source


async def test_publish_event():

    job = CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.com",
        state="Lagos",
        city="Yaba",
        category_slug="restaurants",
    )

    publisher = InMemoryEventPublisher()

    received = []

    async def handler(
        event,
    ):

        received.append(
            event,
        )

    publisher.subscribe(
        handler,
    )

    await publisher.publish(
        PageCrawledEvent(
            job=job,
            page_number=1,
            companies_found=2,
        )
    )

    assert len(
        received,
    ) == 1

    assert isinstance(
        received[0],
        PageCrawledEvent,
    )


async def test_unsubscribe():

    job = CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.com",
        state="Lagos",
        city="Yaba",
        category_slug="restaurants",
    )

    publisher = InMemoryEventPublisher()

    received = []

    async def handler(
        event,
    ):

        received.append(
            event,
        )

    publisher.subscribe(
        handler,
    )

    publisher.unsubscribe(
        handler,
    )

    await publisher.publish(
        PageCrawledEvent(
            job=job,
            page_number=1,
            companies_found=2,
        )
    )

    assert received == []
