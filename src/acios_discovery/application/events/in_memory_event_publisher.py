from __future__ import annotations

from collections.abc import Awaitable, Callable

from acios_discovery.application.events.crawl_event_publisher import (
    CrawlEventPublisher,
)
from acios_discovery.domain.events.crawl_event import (
    CrawlEvent,
)


class InMemoryEventPublisher(
    CrawlEventPublisher,
):
    """
    Simple in-process event publisher.

    All subscribers are notified
    synchronously.
    """

    def __init__(
        self,
    ) -> None:

        self._handlers: list[
            Callable[
                [CrawlEvent],
                Awaitable[None],
            ]
        ] = []

    async def publish(
        self,
        event: CrawlEvent,
    ) -> None:

        for handler in self._handlers:
            await handler(
                event,
            )

    def subscribe(
        self,
        handler,
    ) -> None:

        if handler not in self._handlers:
            self._handlers.append(
                handler,
            )

    def unsubscribe(
        self,
        handler,
    ) -> None:

        if handler in self._handlers:
            self._handlers.remove(
                handler,
            )
