from unittest.mock import AsyncMock

import pytest

from acios_discovery.application.coordination import (
    CrawlCoordinator,
)
from acios_discovery.application.orchestration.result import (
    DiscoveryOrchestrationResult,
)


@pytest.mark.asyncio
async def test_coordinator_runs_orchestrator():

    orchestrator = AsyncMock()

    orchestrator.run.return_value = DiscoveryOrchestrationResult(
        state="Lagos",
        city="Lagos",
        category_slug="restaurants",
        pages_crawled=5,
        companies_discovered=80,
    )

    coordinator = CrawlCoordinator(
        orchestrator=orchestrator,
    )

    result = await coordinator.run(
        state="Lagos",
        city="Lagos",
        category_slug="restaurants",
    )

    orchestrator.run.assert_awaited_once()

    assert result.states == 1

    assert result.cities == 1

    assert result.categories == 1

    assert result.crawl_runs == 1

    assert result.companies_discovered == 80
