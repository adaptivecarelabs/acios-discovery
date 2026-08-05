from __future__ import annotations

from dataclasses import dataclass

from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.events.crawl_event import (
    CrawlEvent,
)


@dataclass(slots=True, kw_only=True)
class PageCrawledEvent(
    CrawlEvent,
):
    """
    Raised whenever a listing page
    has been crawled.
    """

    job: CrawlJob

    page_number: int

    companies_found: int
