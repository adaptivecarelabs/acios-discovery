from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from .crawl_session_status import CrawlSessionStatus


class CrawlSession(BaseModel):
    """
    Represents an entire crawl execution.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    status: CrawlSessionStatus = CrawlSessionStatus.PENDING

    started_at: datetime | None = None

    finished_at: datetime | None = None

    jobs_total: int = 0

    jobs_completed: int = 0

    jobs_failed: int = 0

    retries: int = 0

    pages_crawled: int = 0

    companies_discovered: int = 0

    def start(self) -> None:
        self.status = CrawlSessionStatus.RUNNING
        self.started_at = datetime.now(UTC)

    def complete(self) -> None:
        self.status = CrawlSessionStatus.COMPLETED
        self.finished_at = datetime.now(UTC)

    def fail(self) -> None:
        self.status = CrawlSessionStatus.FAILED
        self.finished_at = datetime.now(UTC)
