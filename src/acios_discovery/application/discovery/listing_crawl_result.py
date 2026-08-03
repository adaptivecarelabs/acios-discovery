from __future__ import annotations

from pydantic import BaseModel


class ListingCrawlResult(BaseModel):
    """
    Summary of a completed listing crawl.
    """

    pages_crawled: int = 0

    companies_discovered: int = 0
