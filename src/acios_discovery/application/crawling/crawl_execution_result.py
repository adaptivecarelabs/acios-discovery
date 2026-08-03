from __future__ import annotations

from pydantic import BaseModel


class CrawlExecutionResult(BaseModel):
    """
    Summary of an execution run.
    """

    jobs_processed: int = 0

    pages_crawled: int = 0

    companies_discovered: int = 0
