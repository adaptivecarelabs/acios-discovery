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
        self.calls = []

    async def execute(
        self,
        job: CrawlJob,
    ) -> DiscoveryRunResult:
        self.calls.append(job)

        return DiscoveryRunResult(
            records_found=2,
            records_saved=2,
            duplicates=0,
            pages_crawled=1,
            source=Source.FINELIB.value,
        )


@pytest.mark.asyncio
async def test_worker_executes_one_job() -> None:
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
    )

    result = await worker.execute(job)

    assert result.pages_crawled == 1
    assert result.companies_discovered == 2

    assert len(pipeline.calls) == 1
    assert pipeline.calls[0] is job
    assert pipeline.calls[0].city == "Yaba"
