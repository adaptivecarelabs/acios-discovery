from __future__ import annotations

from dataclasses import dataclass

from acios_discovery.domain.events.crawl_event import (
    CrawlEvent,
)


@dataclass(slots=True, kw_only=True)
class PageCrawledEvent(
    CrawlEvent,
):
    """
    Raised whenever a page
    has been crawled.
    """
