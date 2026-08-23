from __future__ import annotations

from dataclasses import dataclass

from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.events.crawl_event import CrawlEvent


@dataclass(slots=True, kw_only=True)
class JobFailedEvent(CrawlEvent):
    """
    Raised when a crawl job fails permanently — either a fatal
    (non-retryable) error, or a retryable error that exhausted
    its retry budget.
    """

    job: CrawlJob

    error: str

    retryable: bool
