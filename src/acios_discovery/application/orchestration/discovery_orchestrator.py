from __future__ import annotations

from acios_discovery.application.crawling.crawl_job_factory import (
    CrawlJobFactory,
)
from acios_discovery.application.discovery.pipeline import (
    DiscoveryPipeline,
)
from acios_discovery.application.planning.builders.listing_url_builder import (
    ListingUrlBuilder,
)
from acios_discovery.application.planning.models import CrawlPlan

from .result import DiscoveryOrchestrationResult


class DiscoveryOrchestrator:
    """
    Application entry point for executing one discovery request.

    The orchestrator creates the executable CrawlJob and delegates
    complete discovery execution to DiscoveryPipeline.
    """

    def __init__(
        self,
        *,
        pipeline: DiscoveryPipeline,
        job_factory: CrawlJobFactory,
        listing_builder: ListingUrlBuilder,
    ) -> None:
        self._pipeline = pipeline
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

        result = await self._pipeline.execute(
            job,
        )

        return DiscoveryOrchestrationResult(
            state=state,
            city=city,
            category_slug=category_slug,
            pages_crawled=result.pages_crawled,
            companies_discovered=result.records_found,
        )
