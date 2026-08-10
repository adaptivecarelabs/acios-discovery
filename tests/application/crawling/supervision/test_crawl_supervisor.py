from acios_discovery.application.crawling.supervision.crawl_supervisor import (
    CrawlSupervisor,
)
from acios_discovery.application.crawling.worker_pool_result import (
    WorkerPoolResult,
)
from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
)
from acios_discovery.domain.crawling.crawl_session import (
    CrawlSession,
)
from acios_discovery.domain.crawling.crawl_session_status import (
    CrawlSessionStatus,
)


class FakeWorkerPool:
    async def execute(self):
        return WorkerPoolResult(
            workers=4,
            jobs_processed=10,
            jobs_failed=2,
            pages_crawled=12,
            companies_discovered=36,
            completed=True,
        )



class FailingWorkerPool:
    async def execute(self):
        raise RuntimeError("worker pool failed")



async def test_supervisor_fails_session_when_worker_pool_raises():
    metrics = CrawlMetricsService()

    session = CrawlSession(
        id="session-failed",
    )

    supervisor = CrawlSupervisor(
        session=session,
        worker_pool=FailingWorkerPool(),
        metrics=metrics,
    )

    try:
        await supervisor.run()
    except RuntimeError as exc:
        assert str(exc) == "worker pool failed"
    else:
        raise AssertionError(
            "Expected worker pool failure"
        )

    assert session.status is CrawlSessionStatus.FAILED
    assert session.started_at is not None
    assert session.finished_at is not None




async def test_supervisor_uses_worker_pool_result():
    metrics = CrawlMetricsService()

    # Deliberately make metrics disagree with the worker result.
    for _ in range(99):
        metrics.record_job_processed()

    for _ in range(99):
        metrics.record_page()

    metrics.record_company(999)

    session = CrawlSession(
        id="session-1",
    )

    supervisor = CrawlSupervisor(
        session=session,
        worker_pool=FakeWorkerPool(),
        metrics=metrics,
    )

    result = await supervisor.run()

    assert result.session_id == "session-1"

    assert result.workers == 4
    assert result.jobs_processed == 10
    assert result.pages_crawled == 12
    assert result.companies_discovered == 36

    assert session.status is CrawlSessionStatus.COMPLETED
    assert session.jobs_completed == 10
    assert session.jobs_failed == 2
    assert session.pages_crawled == 12
    assert session.companies_discovered == 36
