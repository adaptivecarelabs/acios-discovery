from __future__ import annotations

from acios_discovery.application.crawling.crawl_job_factory import (
    CrawlJobFactory,
)
from acios_discovery.application.discovery.listing_crawl_engine import (
    ListingCrawlEngine,
)
from acios_discovery.application.planning.builders.listing_url_builder import (
    ListingUrlBuilder,
)
from acios_discovery.application.planning.models import CrawlPlan

from .result import DiscoveryOrchestrationResult


class DiscoveryOrchestrator:
    """
    Application entry point for executing one discovery request.

    The orchestrator converts planning input into an executable
    CrawlJob before handing execution to the crawl engine.
    """

    def __init__(
        self,
        *,
        engine: ListingCrawlEngine,
        job_factory: CrawlJobFactory,
        listing_builder: ListingUrlBuilder,
    ) -> None:
        self._engine = engine
        self._job_factory = job_factory
        self._listing_builder = listing_builder

    async def run(
        self,
        state: str,
        city: str,
        category_slug: str,
    ) -> DiscoveryOrchestrationResult:
        plan = CrawlPlan(
            state=state,
            city=city,
            category_slug=category_slug,
            page=1,
        )

        listing = self._listing_builder.build(
            plan,
        )

        job = self._job_factory.create(
            plan=plan,
            listing=listing,
        )

        crawl_result = await self._engine.execute(
            job,
        )

        return DiscoveryOrchestrationResult(
            state=state,
            city=city,
            category_slug=category_slug,
            pages_crawled=crawl_result.pages_crawled,
            companies_discovered=(
                crawl_result.companies_discovered
            ),
        )
