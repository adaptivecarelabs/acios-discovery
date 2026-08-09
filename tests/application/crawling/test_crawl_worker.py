import pytest

from acios_discovery.application.crawling.crawl_worker import (
    CrawlWorker,
)
from acios_discovery.application.discovery.listing_crawl_result import (
    ListingCrawlResult,
)
from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.sources import Source


class FakeEngine:
    def __init__(self):
        self.calls = []

    async def execute(self, plan):
        self.calls.append(plan)

        return ListingCrawlResult(
            pages_crawled=1,
            companies_discovered=2,
        )


@pytest.mark.asyncio
async def test_worker_executes_one_job():

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
    )

    result = await worker.execute(job)

    assert isinstance(
        result,
        ListingCrawlResult,
    )

    assert len(engine.calls) == 1
    assert engine.calls[0].city == "Yaba"
