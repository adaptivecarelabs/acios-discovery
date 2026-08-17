from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DiscoveryExecutionResult:
    """
    Result of executing one planned discovery operation.
    """

    plans_generated: int

    jobs_submitted: int

    jobs_processed: int

    pages_crawled: int

    companies_discovered: int

    workers: int
