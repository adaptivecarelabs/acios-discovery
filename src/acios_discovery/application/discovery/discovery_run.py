from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DiscoveryRunStatus(str, Enum):
    """
    Lifecycle state of a discovery run.
    """

    CREATED = "CREATED"
    PLANNING = "PLANNING"
    QUEUED = "QUEUED"
    CRAWLING = "CRAWLING"
    ENRICHING = "ENRICHING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class DiscoveryRun:
    """
    Represents one end-to-end discovery execution.

    A DiscoveryRun is intentionally broader than a CrawlSession.

    CrawlSession represents crawl execution.

    DiscoveryRun represents the complete discovery lifecycle:
        planning
        → crawling
        → enrichment
        → processing
        → completion
    """

    run_id: str
    status: DiscoveryRunStatus = DiscoveryRunStatus.CREATED

    total_plans: int = 0
    total_jobs: int = 0

    completed_jobs: int = 0
    failed_jobs: int = 0

    discovered_records: int = 0
    enriched_records: int = 0
    registered_companies: int = 0

    error: str | None = None

    def mark_planning(
        self,
        *,
        total_plans: int,
    ) -> None:
        self.status = DiscoveryRunStatus.PLANNING
        self.total_plans = total_plans

    def mark_queued(
        self,
        *,
        total_jobs: int,
    ) -> None:
        self.status = DiscoveryRunStatus.QUEUED
        self.total_jobs = total_jobs

    def mark_crawling(self) -> None:
        self.status = DiscoveryRunStatus.CRAWLING

    def mark_enriching(self) -> None:
        self.status = DiscoveryRunStatus.ENRICHING

    def mark_processing(self) -> None:
        self.status = DiscoveryRunStatus.PROCESSING

    def mark_completed(
        self,
        *,
        completed_jobs: int,
        failed_jobs: int,
        discovered_records: int,
        enriched_records: int,
        registered_companies: int,
    ) -> None:
        self.status = DiscoveryRunStatus.COMPLETED

        self.completed_jobs = completed_jobs
        self.failed_jobs = failed_jobs
        self.discovered_records = discovered_records
        self.enriched_records = enriched_records
        self.registered_companies = registered_companies

        self.error = None

    def mark_failed(
        self,
        error: str,
    ) -> None:
        self.status = DiscoveryRunStatus.FAILED
        self.error = error

    def mark_cancelled(self) -> None:
        self.status = DiscoveryRunStatus.CANCELLED
