from unittest.mock import AsyncMock

import pytest

from acios_discovery.application.crawling.crawl_job_factory import (
    CrawlJobFactory,
)
from acios_discovery.application.discovery.result import (
    DiscoveryRunResult,
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
    pipeline = AsyncMock()

    pipeline.execute.return_value = DiscoveryRunResult(
        records_found=83,
        records_saved=83,
        duplicates=0,
        pages_crawled=4,
        source="finelib",
    )

    listing_builder = ListingUrlBuilder(
        taxonomy=CategoryProvider(),
        slug_mapper=FinelibUrlSlugMapper(),
    )

    orchestrator = DiscoveryOrchestrator(
        pipeline=pipeline,
        job_factory=CrawlJobFactory(),
        listing_builder=listing_builder,
    )

    result = await orchestrator.run(
        state="Lagos",
        city="Lagos",
        category_slug="restaurants",
    )

    pipeline.execute.assert_awaited_once()

    submitted_job = (
        pipeline.execute.await_args.args[0]
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
