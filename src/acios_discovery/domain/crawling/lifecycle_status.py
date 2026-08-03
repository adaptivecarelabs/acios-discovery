from __future__ import annotations

from enum import StrEnum


class CrawlLifecycleStatus(StrEnum):
    """
    Lifecycle of a crawl job.
    """

    NEW = "NEW"

    QUEUED = "QUEUED"

    RUNNING = "RUNNING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"

    RETRYING = "RETRYING"

    CANCELLED = "CANCELLED"
