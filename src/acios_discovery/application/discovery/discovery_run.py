from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum


class DiscoveryRunStatus(StrEnum):
    """
    Lifecycle state of a discovery run.
    """

    CREATED = "created"
    PLANNING = "planning"
    QUEUED = "queued"
    CRAWLING = "crawling"
    ENRICHING = "enriching"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DiscoveryRun:
    """
    Represents one complete discovery execution.

    A DiscoveryRun tracks the lifecycle of a discovery operation
    from creation through planning, queueing, crawling, enrichment,
    processing, completion, failure, or cancellation.

    The run is intentionally an application-level object.

    It does not perform crawling, persistence, enrichment,
    resolution, or queue management itself.
    """

    def __init__(
        self,
        *,
        run_id: str,
        total_plans: int = 0,
    ) -> None:
        if not run_id:
            raise ValueError("run_id cannot be empty.")

        if total_plans < 0:
            raise ValueError(
                "total_plans cannot be negative."
            )

        self.run_id = run_id
        self.total_plans = total_plans

        self.status = DiscoveryRunStatus.CREATED

        self.created_at = datetime.now(UTC)
        self.started_at: datetime | None = None
        self.finished_at: datetime | None = None

        self.plans_completed = 0
        self.plans_failed = 0

        self._total_jobs = 0
        self.completed_jobs = 0
        self.failed_jobs = 0

        self.discovered_records = 0
        self.enriched_records = 0
        self.registered_companies = 0

        self.error: str | None = None

    @property
    def total_jobs(self) -> int:
        """
        Return the total number of jobs associated with the run.
        """
        return self._total_jobs

    @total_jobs.setter
    def total_jobs(self, value: int) -> None:
        """
        Set the total number of jobs associated with the run.
        """
        if value < 0:
            raise ValueError(
                "total_jobs cannot be negative."
            )

        self._total_jobs = value

    @property
    def is_finished(self) -> bool:
        """
        Return True when the run has reached a terminal state.
        """
        return self.status in {
            DiscoveryRunStatus.COMPLETED,
            DiscoveryRunStatus.FAILED,
            DiscoveryRunStatus.CANCELLED,
        }

    def mark_planning(
        self,
        *,
        total_plans: int | None = None,
    ) -> None:
        """
        Move the run into the planning phase.

        If total_plans is supplied, update the planned workload.
        """
        if total_plans is not None:
            if total_plans < 0:
                raise ValueError(
                    "total_plans cannot be negative."
                )

            self.total_plans = total_plans

        self.status = DiscoveryRunStatus.PLANNING

        if self.started_at is None:
            self.started_at = datetime.now(UTC)

    def mark_queued(
        self,
        *,
        total_jobs: int,
    ) -> None:
        """
        Mark the discovery run as queued for execution.
        """
        if total_jobs < 0:
            raise ValueError(
                "total_jobs cannot be negative."
            )

        self.total_jobs = total_jobs
        self.status = DiscoveryRunStatus.QUEUED

        if self.started_at is None:
            self.started_at = datetime.now(UTC)

    def mark_crawling(self) -> None:
        """
        Mark the discovery run as actively crawling.
        """
        self.status = DiscoveryRunStatus.CRAWLING

        if self.started_at is None:
            self.started_at = datetime.now(UTC)

    def mark_enriching(self) -> None:
        """
        Mark the discovery run as enriching discovered records.
        """
        self.status = DiscoveryRunStatus.ENRICHING

        if self.started_at is None:
            self.started_at = datetime.now(UTC)

    def mark_processing(self) -> None:
        """
        Mark the discovery run as processing discovered data.
        """
        self.status = DiscoveryRunStatus.PROCESSING

        if self.started_at is None:
            self.started_at = datetime.now(UTC)

    def mark_completed(
        self,
        *,
        completed_jobs: int = 0,
        failed_jobs: int = 0,
        discovered_records: int = 0,
        enriched_records: int = 0,
        registered_companies: int = 0,
    ) -> None:
        """
        Mark the discovery run as successfully completed.

        The supplied execution statistics are stored on the run.
        """
        self._validate_non_negative(
            completed_jobs=completed_jobs,
            failed_jobs=failed_jobs,
            discovered_records=discovered_records,
            enriched_records=enriched_records,
            registered_companies=registered_companies,
        )

        self.completed_jobs = completed_jobs
        self.failed_jobs = failed_jobs
        self.discovered_records = discovered_records
        self.enriched_records = enriched_records
        self.registered_companies = registered_companies

        self.status = DiscoveryRunStatus.COMPLETED

        if self.started_at is None:
            self.started_at = datetime.now(UTC)

        self.finished_at = datetime.now(UTC)
        self.error = None

    def mark_failed(self, error: str) -> None:
        """
        Mark the discovery run as failed and record the error.
        """
        if not error:
            raise ValueError(
                "error cannot be empty."
            )

        self.status = DiscoveryRunStatus.FAILED

        if self.started_at is None:
            self.started_at = datetime.now(UTC)

        self.finished_at = datetime.now(UTC)
        self.error = error

    def mark_cancelled(self) -> None:
        """
        Mark the discovery run as cancelled.
        """
        self.status = DiscoveryRunStatus.CANCELLED

        if self.started_at is None:
            self.started_at = datetime.now(UTC)

        self.finished_at = datetime.now(UTC)

    @staticmethod
    def _validate_non_negative(
        **values: int,
    ) -> None:
        """
        Validate that execution counters cannot be negative.
        """
        for name, value in values.items():
            if value < 0:
                raise ValueError(
                    f"{name} cannot be negative."
                )
