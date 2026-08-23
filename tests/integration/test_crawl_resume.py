from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.application.crawling.concurrent_worker_pool import (
    ConcurrentWorkerPool,
)
from acios_discovery.application.crawling.crawl_job_factory import (
    CrawlJobFactory,
)
from acios_discovery.application.crawling.crawl_plan_submission_service import (
    CrawlPlanSubmissionService,
)
from acios_discovery.application.crawling.crawl_worker import CrawlWorker
from acios_discovery.application.crawling.job_scheduler import JobScheduler
from acios_discovery.application.crawling.supervision.crawl_supervisor import (
    CrawlSupervisor,
)
from acios_discovery.application.discovery.discovery_execution_service import (
    DiscoveryExecutionService,
)
from acios_discovery.application.discovery.result import DiscoveryRunResult
from acios_discovery.application.events.in_memory_event_publisher import (
    InMemoryEventPublisher,
)
from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
)
from acios_discovery.application.planning.models import CrawlPlan, ListingUrl
from acios_discovery.application.subscribers.crawl_metrics_subscriber import (
    CrawlMetricsSubscriber,
)
from acios_discovery.domain.crawling.crawl_session import CrawlSession
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.persistence.orm.crawl_session import (
    CrawlSessionORM,
)
from acios_discovery.infrastructure.persistence.repositories.crawl_job_repository import (
    SqlAlchemyCrawlJobRepository,
)
from acios_discovery.infrastructure.persistence.session_scoped_crawl_persistence import (
    SessionScopedCrawlJobPersistence,
    SessionScopedCrawlSessionPersistence,
)
from acios_discovery.infrastructure.queue.in_memory_job_queue import (
    InMemoryJobQueue,
)

TEST_STATE = "Lagos"
FIRST_PLAN = CrawlPlan(state=TEST_STATE, city="Lagos", category_slug="healthcare")
SECOND_PLAN = CrawlPlan(state=TEST_STATE, city="Ikeja", category_slug="healthcare")


class FixedPlanner:
    """Always returns the same two plans, in the same order."""

    def generate(self, *, state: str) -> list[CrawlPlan]:
        return [FIRST_PLAN, SECOND_PLAN]


class FakeListingUrlBuilder:
    """
    Builds a ListingUrl without touching the real Finelib taxonomy
    data — keeps this test hermetic.
    """

    def build(self, plan: CrawlPlan) -> ListingUrl:
        return ListingUrl(
            source=Source.FINELIB,
            url=f"https://example.test/{plan.city}/{plan.category_slug}",
            state=plan.state,
            city=plan.city,
            taxonomy_slug=plan.category_slug,
            page=plan.page,
        )


class SelectivelyFailingPipeline:
    """
    Succeeds for every job except the one whose city is in
    `fail_for_cities` — simulating a crash partway through a
    crawl session for exactly one job.
    """

    def __init__(self, *, fail_for_cities: set[str]) -> None:
        self._fail_for_cities = fail_for_cities

    async def execute(self, job) -> DiscoveryRunResult:

        if job.city in self._fail_for_cities:
            raise RuntimeError(f"Simulated crash processing {job.city}")

        return DiscoveryRunResult(
            records_found=1,
            records_saved=1,
            duplicates=0,
            pages_crawled=1,
            source=job.source.value,
        )


def build_execution_service(
    *,
    db_session: AsyncSession,
    test_session_factory,
    fail_for_cities: set[str],
    resume_session_id: str | None,
) -> tuple[DiscoveryExecutionService, str]:
    """
    Assembles the real orchestration/persistence graph with a fake
    planner, listing builder, and pipeline.
    """

    queue = InMemoryJobQueue()
    scheduler = JobScheduler(queue)
    job_factory = CrawlJobFactory()
    listing_builder = FakeListingUrlBuilder()

    submission_service = CrawlPlanSubmissionService(
        listing_builder=listing_builder,
        job_factory=job_factory,
        scheduler=scheduler,
    )

    publisher = InMemoryEventPublisher()

    metrics_subscriber = CrawlMetricsSubscriber(
        metrics=CrawlMetricsService(),
    )
    publisher.subscribe(metrics_subscriber)

    pipeline = SelectivelyFailingPipeline(fail_for_cities=fail_for_cities)

    def create_worker() -> CrawlWorker:
        return CrawlWorker(
            session_factory=test_session_factory,
            pipeline_factory=lambda _session: pipeline,
        )

    session = (
        CrawlSession(id=resume_session_id)
        if resume_session_id is not None
        else CrawlSession()
    )

    job_persistence = SessionScopedCrawlJobPersistence(
        test_session_factory,
    )

    worker_pool = ConcurrentWorkerPool(
        queue=queue,
        worker_factory=create_worker,
        publisher=publisher,
        workers=1,
        session_id=session.id,
        job_persistence=job_persistence,
    )

    session_persistence = SessionScopedCrawlSessionPersistence(
        test_session_factory,
    )

    supervisor = CrawlSupervisor(
        session=session,
        worker_pool=worker_pool,
        session_persistence=session_persistence,
        resumed=resume_session_id is not None,
    )

    crawl_job_repository = SqlAlchemyCrawlJobRepository(db_session)

    execution_service = DiscoveryExecutionService(
        planner=FixedPlanner(),
        job_submission_service=submission_service,
        crawl_supervisor=supervisor,
        crawl_job_repository=crawl_job_repository,
        resume_session_id=resume_session_id,
    )

    return execution_service, session.id


@pytest.mark.asyncio
async def test_crash_then_resume_skips_completed_work_and_accumulates_counts(
    db_session: AsyncSession,
    test_session_factory,
) -> None:

    #
    # ---------- First run: Ikeja job "crashes" ----------
    #

    first_service, session_id = build_execution_service(
        db_session=db_session,
        test_session_factory=test_session_factory,
        fail_for_cities={"Ikeja"},
        resume_session_id=None,
    )

    first_result = await first_service.run(state=TEST_STATE)

    assert first_result.resumed is False
    assert first_result.plans_generated == 2
    assert first_result.jobs_submitted == 2

    db_session.expire_all()

    session_row = (
        await db_session.execute(
            select(CrawlSessionORM).where(
                CrawlSessionORM.id == session_id,
            )
        )
    ).scalar_one()

    assert session_row.jobs_completed == 1
    assert session_row.jobs_failed == 1

    #
    # ---------- Resume: only the Ikeja job should run ----------
    #
    resumed_service, resumed_session_id = build_execution_service(
        db_session=db_session,
        test_session_factory=test_session_factory,
        fail_for_cities=set(),  # nothing fails this time
        resume_session_id=session_id,
    )

    assert resumed_session_id == session_id

    resumed_result = await resumed_service.run(state=TEST_STATE)

    db_session.expire_all()

    assert resumed_result.resumed is True

    # Lagos already completed in the first run; only Ikeja
    # remained to be submitted.
    assert resumed_result.plans_generated == 1
    assert resumed_result.jobs_submitted == 1

    #
    # ---------- Session counts accumulate across both runs ----------
    #

    final_session_row = (
        await db_session.execute(
            select(CrawlSessionORM).where(
                CrawlSessionORM.id == session_id,
            )
        )
    ).scalar_one()

    # 1 completed + 1 failed from the first run, plus 1 completed
    # from the resumed run: 2 completed, 1 failed total.
    assert final_session_row.jobs_completed == 2
    assert final_session_row.jobs_failed == 1


@pytest.mark.asyncio
async def test_resume_retries_an_early_failed_job_even_if_a_later_job_succeeded(
    db_session: AsyncSession,
    test_session_factory,
) -> None:
    """
    Regression test for the Me Cure Healthcare production incident.

    Lagos is FIRST_PLAN and fails; Ikeja is SECOND_PLAN and
    succeeds. A position-based checkpoint would incorrectly
    treat the run as having progressed past Lagos once Ikeja
    (a later plan) completed, and resume would submit nothing.

    Resume must instead recognize that Lagos specifically never
    completed and resubmit only that plan.
    """

    first_service, session_id = build_execution_service(
        db_session=db_session,
        test_session_factory=test_session_factory,
        fail_for_cities={"Lagos"},
        resume_session_id=None,
    )

    first_result = await first_service.run(state=TEST_STATE)

    assert first_result.resumed is False
    assert first_result.plans_generated == 2
    assert first_result.jobs_submitted == 2

    db_session.expire_all()

    session_row = (
        await db_session.execute(
            select(CrawlSessionORM).where(
                CrawlSessionORM.id == session_id,
            )
        )
    ).scalar_one()

    assert session_row.jobs_completed == 1  # Ikeja
    assert session_row.jobs_failed == 1  # Lagos

    resumed_service, resumed_session_id = build_execution_service(
        db_session=db_session,
        test_session_factory=test_session_factory,
        fail_for_cities=set(),
        resume_session_id=session_id,
    )

    resumed_result = await resumed_service.run(state=TEST_STATE)

    assert resumed_result.resumed is True
    assert resumed_result.plans_generated == 1
    assert resumed_result.jobs_submitted == 1

    db_session.expire_all()

    final_session_row = (
        await db_session.execute(
            select(CrawlSessionORM).where(
                CrawlSessionORM.id == session_id,
            )
        )
    ).scalar_one()

    assert final_session_row.jobs_completed == 2
    assert final_session_row.jobs_failed == 1
