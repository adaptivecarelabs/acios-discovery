from __future__ import annotations

from dataclasses import dataclass

from acios_discovery.domain.crawling import CrawlJob
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

    job: CrawlJob

    pages_crawled: int

    companies_discovered: int
