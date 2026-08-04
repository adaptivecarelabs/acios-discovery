from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CrawlSupervisorResult:
    """
    Overall result produced after a crawl session
    has completed.
    """

    session_id: str

    workers: int

    jobs_processed: int

    pages_crawled: int

    companies_discovered: int
