from acios_discovery.application.orchestration import (
    DiscoveryOrchestrator,
)

from .result import CrawlCoordinatorResult


class CrawlCoordinator:
    """
    Coordinates discovery runs.

    Currently executes a single run.
    Later it will execute thousands.
    """

    def __init__(
        self,
        orchestrator: DiscoveryOrchestrator,
    ) -> None:

        self._orchestrator = orchestrator

    async def run(
        self,
        *,
        state: str,
        city: str,
        category_slug: str,
    ) -> CrawlCoordinatorResult:

        result = await self._orchestrator.run(
            state=state,
            city=city,
            category_slug=category_slug,
        )

        return CrawlCoordinatorResult(
            states=1,
            cities=1,
            categories=1,
            crawl_runs=1,
            companies_discovered=result.companies_discovered,
        )
