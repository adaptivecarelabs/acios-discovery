from __future__ import annotations

from enum import StrEnum


class CrawlState(StrEnum):
    """
    Lifecycle states for a crawl execution.
    """

    CREATED = "CREATED"

    INITIALIZING = "INITIALIZING"

    RUNNING = "RUNNING"

    PAUSED = "PAUSED"

    RESUMING = "RESUMING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"

    CANCELLED = "CANCELLED"
