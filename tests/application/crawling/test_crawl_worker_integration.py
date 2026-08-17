from __future__ import annotations

import pytest

from acios_discovery.application.crawling.crawl_worker import (
    CrawlWorker,
)
from acios_discovery.application.discovery.result import (
    DiscoveryRunResult,
)
from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.sources import Source


class FakeSession:
    def __init__(self) -> None:
        self.committed = False

    async def __aenter__(self) -> FakeSession:
        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:
        return None

    async def commit(self) -> None:
        self.committed = True


class FakePipeline:
    def __init__(self) -> None:
        self.jobs: list[CrawlJob] = []

    async def execute(
        self,
        job: CrawlJob,
    ) -> DiscoveryRunResult:
        self.jobs.append(job)

        return DiscoveryRunResult(
            records_found=0,
            records_saved=0,
            duplicates=0,
            pages_crawled=1,
            source=Source.FINELIB.value,
        )


@pytest.mark.asyncio
async def test_worker_passes_crawl_job_to_pipeline() -> None:
    pipeline = FakePipeline()
    session = FakeSession()

    worker = CrawlWorker(
        session_factory=lambda: session,  # type: ignore[arg-type]
        pipeline_factory=lambda _session: pipeline,
    )

    job = CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.com",
        state="Lagos",
        city="Yaba",
        category_slug="restaurants",
        page=3,
    )

    result = await worker.execute(job)

    assert result.pages_crawled == 1

    assert len(pipeline.jobs) == 1

    assert pipeline.jobs[0] is job
    assert pipeline.jobs[0].city == "Yaba"
    assert pipeline.jobs[0].page == 3

    assert session.committed is True
