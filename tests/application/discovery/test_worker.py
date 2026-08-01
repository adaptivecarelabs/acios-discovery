import pytest

from acios_discovery.application.crawling.worker import CrawlWorker
from acios_discovery.application.discovery.result import (
    DiscoveryRunResult,
)
from acios_discovery.domain.crawling.job import CrawlJob
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


class FakeDiscoveryService:
    def __init__(self, result: DiscoveryRunResult):
        self._result = result
        self.called_with = None

    async def run(self, job):
        self.called_with = job
        return self._result



@pytest.mark.asyncio
async def test_worker_saves_new_records(
    sample_discovery_record,
):

    queue = InMemoryJobQueue()

    job = CrawlJob(
        source="finelib",
        listing_url="https://example.com",
        state="Lagos",
        city="Lagos",
        category_slug="health",
    )

    await queue.enqueue(job)

    service = FakeDiscoveryService(
        DiscoveryRunResult(
            source="finelib",
            records_found=1,
            records_saved=1,
            duplicates=0,
        )
    )

    worker = CrawlWorker(
        service=service,
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

    assert service.called_with == job
    assert job.status.name == "COMPLETED"

    assert await queue.dequeue() is None
