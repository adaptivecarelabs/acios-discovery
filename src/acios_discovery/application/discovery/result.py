from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class DiscoveryRunResult:
    """
    Result of processing one complete discovery crawl job.

    This is the application-level result consumed by
    CrawlWorker, CrawlExecutor, and ConcurrentWorkerPool.
    """

    source: str

    pages_crawled: int = 0
    records_found: int = 0
    records_saved: int = 0
    duplicates: int = 0

    errors: list[str] = field(default_factory=list)

    @property
    def companies_discovered(self) -> int:
        """
        Compatibility alias for callers that use the
        crawl terminology.
        """
        return self.records_found
