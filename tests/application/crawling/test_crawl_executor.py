import pytest

from acios_discovery.application.crawling.crawl_execution_result import (
    CrawlExecutionResult,
)
from acios_discovery.application.crawling.crawl_executor import (
    CrawlExecutor,
)
from acios_discovery.application.discovery.listing_crawl_result import (
    ListingCrawlResult,
)
from acios_discovery.domain.crawling import (
    CrawlJob,
)
from acios_discovery.domain.sources import (
    Source,
)
from acios_discovery.infrastructure.queue.in_memory_job_queue import (
    InMemoryJobQueue,
)


class FakeWorker:

    async def execute(
        self,
        job,
    ):

        return ListingCrawlResult(
            pages_crawled=2,
            companies_discovered=10,
        )


@pytest.mark.asyncio
async def test_executor_processes_all_jobs():

    queue = InMemoryJobQueue()

    await queue.enqueue(
        CrawlJob(
            source=Source.FINELIB,
            listing_url="https://example.com/1",
            state="Lagos",
            city="Yaba",
            category_slug="restaurants",
        )
    )

    await queue.enqueue(
        CrawlJob(
            source=Source.FINELIB,
            listing_url="https://example.com/2",
            state="Lagos",
            city="Lekki",
            category_slug="banks",
        )
    )

    executor = CrawlExecutor(
        queue=queue,
        worker=FakeWorker(),
    )

    result = await executor.execute()

    assert isinstance(
        result,
        CrawlExecutionResult,
    )

    assert result.jobs_processed == 2

    assert result.pages_crawled == 4

    assert result.companies_discovered == 20
