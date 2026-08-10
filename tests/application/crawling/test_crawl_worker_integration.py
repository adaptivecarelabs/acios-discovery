import pytest

from acios_discovery.application.crawling.crawl_worker import (
    CrawlWorker,
)
from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.sources import Source


@pytest.mark.asyncio
async def test_worker_passes_crawl_job_to_engine() -> None:
    class FakeEngine:
        def __init__(self) -> None:
            self.jobs = []

        async def execute(self, job):
            self.jobs.append(job)

            from acios_discovery.application.discovery.listing_crawl_result import (
                ListingCrawlResult,
            )

            return ListingCrawlResult(
                pages_crawled=1,
                companies_discovered=0,
            )

    engine = FakeEngine()

    worker = CrawlWorker(
        engine=engine,
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

    assert len(engine.jobs) == 1

    assert engine.jobs[0] is job

    assert engine.jobs[0].city == "Yaba"

    assert engine.jobs[0].page == 3
