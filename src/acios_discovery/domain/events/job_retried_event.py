from __future__ import annotations

from dataclasses import dataclass

from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.events.crawl_event import CrawlEvent


@dataclass(slots=True, kw_only=True)
class JobRetriedEvent(CrawlEvent):
    """
    Raised when a crawl job fails with a retryable error and is
    about to be retried in place.
    """

    job: CrawlJob

    attempt: int

    max_retries: int

    error: str
