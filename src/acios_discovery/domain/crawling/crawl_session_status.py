from enum import StrEnum


class CrawlSessionStatus(StrEnum):
    """
    Overall state of a crawl session.
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
