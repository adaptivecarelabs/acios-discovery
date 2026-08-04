from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class CrawlMetrics:
    """
    Runtime metrics collected while
    a crawl is executing.
    """

    started_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    finished_at: datetime | None = None

    jobs_processed: int = 0

    pages_crawled: int = 0

    companies_discovered: int = 0

    requests_sent: int = 0

    retries: int = 0

    failures: int = 0

    successful_requests: int = 0
