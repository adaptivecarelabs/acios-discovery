from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CrawlExecutionResult:
    """
    Aggregate result of sequential crawl execution.
    """

    jobs_processed: int = 0
    pages_crawled: int = 0
    companies_discovered: int = 0
    jobs_failed: int = 0
