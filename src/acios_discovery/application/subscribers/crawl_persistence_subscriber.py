from __future__ import annotations

from acios_discovery.domain.events.crawl_event import (
    CrawlEvent,
)


class CrawlPersistenceSubscriber:
    """
    Receives crawl events.

    Persistence will be implemented
    in the next phase.

    For now this subscriber simply
    stores every event that it
    receives so that we can verify
    the event pipeline.
    """

    def __init__(
        self,
    ) -> None:

        self.events: list[CrawlEvent] = []

    async def __call__(
        self,
        event: CrawlEvent,
    ) -> None:

        self.events.append(
            event,
        )
