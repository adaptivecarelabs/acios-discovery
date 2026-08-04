from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WorkerPoolResult:
    """
    Result returned after the worker
    pool finishes execution.

    Runtime statistics are owned by
    CrawlMetricsService.
    """

    workers: int = 0

    completed: bool = False
