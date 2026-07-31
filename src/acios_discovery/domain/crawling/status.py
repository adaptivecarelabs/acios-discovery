from enum import StrEnum


class CrawlStatus(StrEnum):
    """
    Current state of a crawl job.
    """

    PENDING = "pending"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    RETRYING = "retrying"

    CANCELLED = "cancelled"
