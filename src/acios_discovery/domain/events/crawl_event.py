from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True, kw_only=True)
class CrawlEvent:
    """
    Base class for every crawl event.

    Every event automatically records
    when it occurred.
    """

    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    @property
    def event_type(self) -> str:
        return self.__class__.__name__
