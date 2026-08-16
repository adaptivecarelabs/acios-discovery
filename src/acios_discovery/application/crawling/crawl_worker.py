from __future__ import annotations

from acios_discovery.application.discovery.listing_crawl_result import (
    ListingCrawlResult,
)
from acios_discovery.application.discovery.pipeline import (
    DiscoveryPipeline,
)
from acios_discovery.domain.crawling import CrawlJob


class CrawlWorker:
    """
    Executes one CrawlJob through the authoritative
    DiscoveryPipeline.

    The worker does not perform crawling itself.
    It delegates the complete discovery lifecycle to
    DiscoveryPipeline.
    """

    def __init__(
        self,
        *,
        pipeline: DiscoveryPipeline,
    ) -> None:
        self._pipeline = pipeline

    async def execute(
        self,
        job: CrawlJob,
    ) -> ListingCrawlResult:
        result = await self._pipeline.execute(
            job,
        )

        return ListingCrawlResult(
            pages_crawled=result.pages_crawled,
            companies_discovered=result.records_found,
        )
