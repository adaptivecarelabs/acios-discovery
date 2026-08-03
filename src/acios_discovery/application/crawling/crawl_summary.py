from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CrawlSummary(BaseModel):
    """
    High-level summary of a crawl execution.
    """

    started_at: datetime

    finished_at: datetime

    jobs_processed: int = 0

    jobs_failed: int = 0

    pages_crawled: int = 0

    companies_discovered: int = 0

    @property
    def duration_seconds(
        self,
    ) -> float:

        return (
            self.finished_at
            - self.started_at
        ).total_seconds()
