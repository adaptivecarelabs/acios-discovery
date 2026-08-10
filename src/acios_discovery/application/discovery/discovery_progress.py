from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DiscoveryProgress:
    """
    Snapshot of discovery execution progress.

    This object is intentionally immutable.

    A coordinator can create a new snapshot whenever execution
    state changes without exposing mutable internal state.
    """

    total_plans: int = 0
    total_jobs: int = 0

    queued_jobs: int = 0
    running_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0

    discovered_records: int = 0
    enriched_records: int = 0
    registered_companies: int = 0

    @property
    def finished_jobs(self) -> int:
        """
        Number of jobs that have reached a terminal state.
        """
        return (
            self.completed_jobs
            + self.failed_jobs
        )

    @property
    def remaining_jobs(self) -> int:
        """
        Number of jobs that have not yet reached a terminal state.
        """
        return max(
            0,
            self.total_jobs - self.finished_jobs,
        )

    @property
    def is_complete(self) -> bool:
        """
        Whether all known jobs have finished.
        """
        return (
            self.total_jobs > 0
            and self.remaining_jobs == 0
        )
