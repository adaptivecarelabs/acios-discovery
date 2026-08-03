from __future__ import annotations

from acios_discovery.application.discovery.listing_crawl_engine import (
    ListingCrawlEngine,
)
from acios_discovery.application.discovery.listing_crawl_result import (
    ListingCrawlResult,
)
from acios_discovery.application.planning.models import (
    CrawlPlan,
)
from acios_discovery.domain.crawling import (
    CrawlJob,
)


class CrawlWorker:
    """
    Executes a single crawl job.
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

        plan = CrawlPlan(
            state=job.state,
            city=job.city,
            category_slug=job.category_slug,
            page=job.page,
        )

        return await self._engine.execute(
            plan,
        )
