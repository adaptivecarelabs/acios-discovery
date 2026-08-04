from acios_discovery.application.events.in_memory_event_publisher import (
    InMemoryEventPublisher,
)
from acios_discovery.domain.events.page_crawled_event import (
    PageCrawledEvent,
)


def test_publish_event():

    publisher = InMemoryEventPublisher()

    received = []

    def handler(
        event,
    ):

        received.append(
            event,
        )

    publisher.subscribe(
        handler,
    )

    publisher.publish(
        PageCrawledEvent(),
    )

    assert len(
        received,
    ) == 1

    assert isinstance(
        received[0],
        PageCrawledEvent,
    )


def test_unsubscribe():

    publisher = InMemoryEventPublisher()

    received = []

    def handler(
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

    publisher.publish(
        PageCrawledEvent(),
    )

    assert received == []
