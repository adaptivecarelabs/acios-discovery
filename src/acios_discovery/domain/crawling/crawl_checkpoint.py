from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class CrawlCheckpoint:
    """
    Stores crawler progress so execution
    can resume after interruption.
    """

    session_id: str

    state: str

    city: str

    category_slug: str

    page: int

    company_index: int = 0

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )
