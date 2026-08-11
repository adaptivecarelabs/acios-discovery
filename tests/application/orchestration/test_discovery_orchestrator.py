from unittest.mock import AsyncMock

import pytest

from acios_discovery.application.crawling.crawl_job_factory import (
    CrawlJobFactory,
)
from acios_discovery.application.discovery.listing_crawl_result import (
    ListingCrawlResult,
)
from acios_discovery.application.orchestration import (
    DiscoveryOrchestrator,
)
from acios_discovery.application.planning.builders.listing_url_builder import (
    ListingUrlBuilder,
)
from acios_discovery.application.planning.providers.category_provider import (
    CategoryProvider,
)
from acios_discovery.infrastructure.connectors.finelib.url_slug_mapper import (
    FinelibUrlSlugMapper,
)


@pytest.mark.asyncio
async def test_orchestrator_runs_engine() -> None:
    engine = AsyncMock()

    engine.execute.return_value = ListingCrawlResult(
        pages_crawled=4,
        companies_discovered=83,
    )

    listing_builder = ListingUrlBuilder(
        taxonomy=CategoryProvider(),
        slug_mapper=FinelibUrlSlugMapper(),
    )

    orchestrator = DiscoveryOrchestrator(
        engine=engine,
        job_factory=CrawlJobFactory(),
        listing_builder=listing_builder,
    )

    result = await orchestrator.run(
        state="Lagos",
        city="Lagos",
        category_slug="restaurants",
    )

    engine.execute.assert_awaited_once()

    submitted_job = (
        engine.execute.await_args.args[0]
    )

    assert submitted_job.state == "Lagos"
    assert submitted_job.city == "Lagos"
    assert submitted_job.category_slug == "restaurants"
    assert submitted_job.page == 1

    assert result.state == "Lagos"
    assert result.city == "Lagos"
    assert result.category_slug == "restaurants"
    assert result.pages_crawled == 4
    assert result.companies_discovered == 83
