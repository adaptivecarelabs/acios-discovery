from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WorkerPoolResult:
    """
    Result returned after the worker pool finishes execution.

    The pool owns execution-level statistics.
    """

    workers: int = 0
    jobs_processed: int = 0
    pages_crawled: int = 0
    companies_discovered: int = 0
    jobs_failed: int = 0
    enrichment_failures: int = 0
    completed: bool = False
