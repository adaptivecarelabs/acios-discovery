from __future__ import annotations

from dataclasses import dataclass

from acios_discovery.domain.events.crawl_event import (
    CrawlEvent,
)


@dataclass(slots=True, kw_only=True)
class JobCompletedEvent(
    CrawlEvent,
):
    """
    Raised after a crawl job
    has completed.
    """

    jobs_completed: int = 1
