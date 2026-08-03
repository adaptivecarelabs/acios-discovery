from acios_discovery.application.discovery.listing_crawl_engine import (
    ListingCrawlEngine,
)
from acios_discovery.application.planning.models import (
    CrawlPlan,
)

from .result import DiscoveryOrchestrationResult


class DiscoveryOrchestrator:

    def __init__(
        self,
        engine: ListingCrawlEngine,
    ) -> None:

        self._engine = engine

    async def run(
        self,
        state: str,
        city: str,
        category_slug: str,
    ) -> DiscoveryOrchestrationResult:

        crawl_result = await self._engine.execute(
            CrawlPlan(
                state=state,
                city=city,
                category_slug=category_slug,
            )
        )

        return DiscoveryOrchestrationResult(
            state=state,
            city=city,
            category_slug=category_slug,
            pages_crawled=crawl_result.pages_crawled,
            companies_discovered=crawl_result.companies_discovered,
        )
