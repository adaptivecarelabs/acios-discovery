from __future__ import annotations

from acios_discovery.application.discovery.discovery_execution_service import (
    DiscoveryExecutionService,
)
from acios_discovery.domain.crawling.job import CrawlJob
from acios_discovery.domain.crawling.priority import CrawlPriority
from acios_discovery.domain.crawling.status import CrawlStatus
from acios_discovery.domain.sources.source import Source


class FakePlanner:
    def generate(
        self,
        *,
        state: str,
    ):
        from acios_discovery.application.planning.models import (
            CrawlPlan,
        )

        return [
            CrawlPlan(
                state=state,
                city="Lagos",
                category_slug="healthcare",
                page=1,
            ),
            CrawlPlan(
                state=state,
                city="Ikeja",
                category_slug="healthcare",
                page=1,
            ),
        ]


class FakeSubmissionService:
    def __init__(self) -> None:
        self.submitted_plans = None

    async def submit(
        self,
        plans,
    ) -> int:
        self.submitted_plans = plans
        return len(plans)


class FakeSupervisor:
    async def run(self):
        return type(
            "SupervisorResult",
            (),
            {
                "session_id": "fake-session-id",
                "workers": 4,
                "jobs_processed": 3,
                "pages_crawled": 7,
                "companies_discovered": 42,
            },
        )()


def make_job(
    *,
    city: str,
    category_slug: str,
    page: int = 1,
    status: CrawlStatus,
) -> CrawlJob:
    return CrawlJob(
        id=f"{city}-{category_slug}-{page}",
        source=Source.FINELIB,
        listing_url="https://example.com",
        state="Lagos",
        city=city,
        category_slug=category_slug,
        page=page,
        priority=CrawlPriority.NORMAL,
        retries=0,
        max_retries=3,
        status=status,
    )


class FakeCrawlJobRepository:
    def __init__(
        self,
        jobs: list[CrawlJob],
    ) -> None:
        self._jobs = jobs

    async def list_by_session(
        self,
        session_id: str,
    ) -> list[CrawlJob]:
        return self._jobs


async def test_execution_service_coordinates_discovery() -> None:
    submission_service = FakeSubmissionService()

    service = DiscoveryExecutionService(
        planner=FakePlanner(),
        job_submission_service=submission_service,
        crawl_supervisor=FakeSupervisor(),
        crawl_job_repository=FakeCrawlJobRepository([]),
        # resume_session_id is None: crawl_job_repository never called
    )

    result = await service.run(
        state="Lagos",
    )

    assert result.plans_generated == 2
    assert result.jobs_submitted == 2
    assert result.jobs_processed == 3
    assert result.pages_crawled == 7
    assert result.companies_discovered == 42
    assert result.workers == 4


async def test_resume_skips_only_completed_plans_regardless_of_order() -> None:
    """
    Regression test for the Lagos/Ikeja resume incident.

    A failed job followed later by a successful job for a
    DIFFERENT (city, category_slug) must not cause the failed
    job's plan to be skipped on resume — the resume model is
    per-(city, category_slug, page), not "furthest position
    reached in the plan list".
    """

    submission_service = FakeSubmissionService()

    jobs = [
        make_job(
            city="Lagos",
            category_slug="healthcare",
            status=CrawlStatus.FAILED,
        ),
        make_job(
            city="Ikeja",
            category_slug="healthcare",
            status=CrawlStatus.COMPLETED,
        ),
    ]

    service = DiscoveryExecutionService(
        planner=FakePlanner(),
        job_submission_service=submission_service,
        crawl_supervisor=FakeSupervisor(),
        crawl_job_repository=FakeCrawlJobRepository(jobs),
        resume_session_id="some-session-id",
    )

    result = await service.run(
        state="Lagos",
    )

    assert result.resumed is True
    assert result.plans_generated == 1

    assert len(submission_service.submitted_plans) == 1
    assert submission_service.submitted_plans[0].city == "Lagos"
    assert submission_service.submitted_plans[0].category_slug == "healthcare"


async def test_resume_skips_completed_plans() -> None:

    submission_service = FakeSubmissionService()

    jobs = [
        make_job(
            city="Lagos",
            category_slug="healthcare",
            status=CrawlStatus.COMPLETED,
        ),
        make_job(
            city="Ikeja",
            category_slug="healthcare",
            status=CrawlStatus.COMPLETED,
        ),
    ]

    service = DiscoveryExecutionService(
        planner=FakePlanner(),
        job_submission_service=submission_service,
        crawl_supervisor=FakeSupervisor(),
        crawl_job_repository=FakeCrawlJobRepository(jobs),
        resume_session_id="some-session-id",
    )

    result = await service.run(
        state="Lagos",
    )

    assert result.resumed is True
    assert result.plans_generated == 0
    assert submission_service.submitted_plans == []
