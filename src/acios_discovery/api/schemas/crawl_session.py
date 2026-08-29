from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class StartCrawlRequest(BaseModel):
    state: str
    categories: list[str] | None = None
    max_jobs: int | None = None


class CrawlSessionResponse(BaseModel):
    id: str
    state: str | None
    categories: list[str] | None
    max_jobs: int | None
    triggered_by_user_id: str | None
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    jobs_total: int
    jobs_completed: int
    jobs_failed: int
    pages_crawled: int
    companies_discovered: int
