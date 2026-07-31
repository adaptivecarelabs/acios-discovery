from enum import IntEnum


class CrawlPriority(IntEnum):
    """
    Lower value means higher priority.
    """

    HIGH = 1

    NORMAL = 5

    LOW = 10
