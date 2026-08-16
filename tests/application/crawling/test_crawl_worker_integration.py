import pytest

from acios_discovery.application.crawling.crawl_worker import (
    CrawlWorker,
)
from acios_discovery.application.discovery.result import (
    DiscoveryRunResult,
)
from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.sources import Source


class FakePipeline:
    def __init__(self) -> None:
        self.jobs = []

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

    worker = CrawlWorker(
        pipeline=pipeline,
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
