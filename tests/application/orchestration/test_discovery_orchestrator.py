from unittest.mock import AsyncMock

import pytest

from acios_discovery.application.discovery.listing_crawl_result import (
    ListingCrawlResult,
)
from acios_discovery.application.orchestration import (
    DiscoveryOrchestrator,
)


@pytest.mark.asyncio
async def test_orchestrator_runs_engine():

    engine = AsyncMock()

    engine.execute.return_value = ListingCrawlResult(
        pages_crawled=4,
        companies_discovered=83,
    )

    orchestrator = DiscoveryOrchestrator(
        engine=engine,
    )

    result = await orchestrator.run(
        state="Lagos",
        city="Lagos",
        category_slug="restaurants",
    )

    engine.execute.assert_awaited_once()

    assert result.state == "Lagos"

    assert result.city == "Lagos"

    assert result.category_slug == "restaurants"

    assert result.pages_crawled == 4

    assert result.companies_discovered == 83
