from __future__ import annotations

from abc import ABC, abstractmethod

from acios_discovery.domain.events.crawl_event import (
    CrawlEvent,
)


class CrawlEventPublisher(
    ABC,
):
    """
    Contract for publishing crawl events.

    Implementations decide how events
    are delivered to subscribers.
    """

    @abstractmethod
    async def publish(
        self,
        event: CrawlEvent,
    ) -> None:
        """
        Publish an event.
        """

    @abstractmethod
    def subscribe(
        self,
        handler,
    ) -> None:
        """
        Register an event handler.
        """

    @abstractmethod
    def unsubscribe(
        self,
        handler,
    ) -> None:
        """
        Remove an event handler.
        """
