import pytest

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


class FakeWorkerPool:

    async def execute(self):

        return WorkerPoolResult(
            workers=4,
            completed=True,
        )


@pytest.mark.asyncio
async def test_supervisor_runs_worker_pool():

    metrics = CrawlMetricsService()

    for _ in range(10):
        metrics.record_job_processed()

    for _ in range(12):
        metrics.record_page()

    metrics.record_company(36)

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
