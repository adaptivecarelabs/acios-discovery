import pytest

from acios_discovery.application.crawling.worker import CrawlWorker
from acios_discovery.application.discovery.result import (
    DiscoveryRunResult,
)
from acios_discovery.domain.crawling.job import CrawlJob
from acios_discovery.infrastructure.persistence.in_memory_discovery_repository import (
    InMemoryDiscoveryRepository,
)
from acios_discovery.infrastructure.queue.in_memory_job_queue import (
    InMemoryJobQueue,
)


class FakeConnector:
    def __init__(
        self,
        records,
    ):
        self._records = records

    async def crawl(
        self,
        job,
    ):
        return self._records


@pytest.mark.asyncio
async def test_worker_saves_new_records(
    sample_discovery_record,
):

    repository = InMemoryDiscoveryRepository()

    queue = InMemoryJobQueue()

    job = CrawlJob(
        source="finelib",
        listing_url="https://example.com",
        state="Lagos",
        city="Lagos",
        category_slug="health",
    )

    await queue.enqueue(job)

    connector = FakeConnector(
        [sample_discovery_record],
    )

    worker = CrawlWorker(
        connector=connector,
        repository=repository,
        queue=queue,
    )

    result = await worker.run_one_job()

    assert isinstance(
        result,
        DiscoveryRunResult,
    )

    assert result.records_found == 1
    assert result.records_saved == 1
    assert result.duplicates == 0

    assert await repository.count() == 1

    assert await queue.dequeue() is None
