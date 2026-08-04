from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(slots=True, kw_only=True)
class CrawlEvent:
    """
    Base class for every crawl event.

    Every event automatically records
    when it occurred.
    """

    occurred_at: datetime = datetime.now(
        UTC,
    )
