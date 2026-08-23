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
from acios_discovery.application.planning.models import CrawlPlan
from acios_discovery.domain.crawling.status import CrawlStatus
from acios_discovery.domain.repositories.crawl_job_repository import (
    CrawlJobRepository,
)

from .discovery_execution_result import (
    DiscoveryExecutionResult,
)


class DiscoveryExecutionService:
    """
    Coordinates one complete discovery execution.

    Responsibilities:

        1. Generate crawl plans.
        2. If resuming, skip plans whose (city, category_slug)
           already completed successfully in the session being
           resumed, based on persisted crawl job status.
        3. Submit crawl jobs.
        4. Supervise execution of the submitted jobs.

    It does not perform crawling itself.

    Crawling is delegated to the crawl execution subsystem.

    Resume is order-independent: it does not assume plans
    complete in submission order. A job that failed does not
    cause later, unrelated (city, category_slug) plans to be
    skipped on resume, and a job that failed is retried on
    resume even if later plans in the same original run
    completed successfully.
    """

    def __init__(
        self,
        *,
        planner: CrawlPlanGenerator,
        job_submission_service: CrawlPlanSubmissionService,
        crawl_supervisor: CrawlSupervisor,
        crawl_job_repository: CrawlJobRepository,
        resume_session_id: str | None = None,
    ) -> None:
        self._planner = planner
        self._job_submission_service = (
            job_submission_service
        )
        self._crawl_supervisor = crawl_supervisor
        self._crawl_job_repository = crawl_job_repository
        self._resume_session_id = resume_session_id

    @staticmethod
    def _plan_key(
        plan: CrawlPlan,
    ) -> tuple[str, str, int]:
        return (
            plan.city,
            plan.category_slug,
            plan.page,
        )

    async def _remaining_plans(
        self,
        plans: list[CrawlPlan],
    ) -> list[CrawlPlan]:
        """
        Return only the plans that have not already completed
        successfully in the session being resumed.

        A plan is considered done only if a crawl job for the
        exact same (city, category_slug, page) reached
        CrawlStatus.COMPLETED. Failed, cancelled, or otherwise
        incomplete jobs are NOT treated as done, so their plans
        are resubmitted regardless of where they fall in the
        plan list relative to other, successful jobs.
        """

        jobs = await self._crawl_job_repository.list_by_session(
            self._resume_session_id,
        )

        completed = {
            (job.city, job.category_slug, job.page)
            for job in jobs
            if job.status == CrawlStatus.COMPLETED
        }

        return [
            plan
            for plan in plans
            if self._plan_key(plan) not in completed
        ]

    async def run(
        self,
        *,
        state: str,
    ) -> DiscoveryExecutionResult:

        plans = self._planner.generate(
            state=state,
        )

        resumed = False

        if self._resume_session_id is not None:

            plans = await self._remaining_plans(
                plans,
            )

            resumed = True

        submitted = await self._job_submission_service.submit(
            plans,
        )

        supervisor_result = await self._crawl_supervisor.run()

        return DiscoveryExecutionResult(
            session_id=supervisor_result.session_id,
            resumed=resumed,
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
