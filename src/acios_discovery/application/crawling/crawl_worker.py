from __future__ import annotations

from acios_discovery.application.discovery.listing_crawl_engine import (
    ListingCrawlEngine,
)
from acios_discovery.application.discovery.listing_crawl_result import (
    ListingCrawlResult,
)
from acios_discovery.domain.crawling import CrawlJob


class CrawlWorker:
    """
    Executes one CrawlJob through the configured crawl engine.
    """

    def __init__(
        self,
        *,
        engine: ListingCrawlEngine,
    ) -> None:
        self._engine = engine

    async def execute(
        self,
        job: CrawlJob,
    ) -> ListingCrawlResult:
        return await self._engine.execute(job)
