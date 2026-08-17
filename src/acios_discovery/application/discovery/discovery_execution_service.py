from __future__ import annotations

from acios_discovery.application.crawling.crawl_plan_submission_service import (
    CrawlPlanSubmissionService,
)
from acios_discovery.application.crawling.supervision.crawl_supervisor import (
    CrawlSupervisor,
)
from acios_discovery.application.planning.crawl_plan_generator import (
    CrawlPlanGenerator,
)

from .discovery_execution_result import (
    DiscoveryExecutionResult,
)


class DiscoveryExecutionService:
    """
    Coordinates one complete discovery execution.

    Responsibilities:

        1. Generate crawl plans.
        2. Submit crawl jobs.
        3. Supervise execution of the submitted jobs.

    It does not perform crawling itself.

    Crawling is delegated to the crawl execution subsystem.
    """

    def __init__(
        self,
        *,
        planner: CrawlPlanGenerator,
        job_submission_service: CrawlPlanSubmissionService,
        crawl_supervisor: CrawlSupervisor,
    ) -> None:
        self._planner = planner
        self._job_submission_service = (
            job_submission_service
        )
        self._crawl_supervisor = crawl_supervisor

    async def run(
        self,
        *,
        state: str,
    ) -> DiscoveryExecutionResult:
        plans = self._planner.generate(
            state=state,
        )

        submitted = await self._job_submission_service.submit(
            plans,
        )

        supervisor_result = await self._crawl_supervisor.run()

        return DiscoveryExecutionResult(
            plans_generated=len(plans),
            jobs_submitted=submitted,
            jobs_processed=(
                supervisor_result.jobs_processed
            ),
            pages_crawled=(
                supervisor_result.pages_crawled
            ),
            companies_discovered=(
                supervisor_result.companies_discovered
            ),
            workers=supervisor_result.workers,
        )
