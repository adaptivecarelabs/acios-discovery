import pytest

from acios_discovery.application.crawling.job_scheduler import (
    JobScheduler,
)
from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.queue.in_memory_job_queue import (
    InMemoryJobQueue,
)


@pytest.mark.asyncio
async def test_schedules_jobs():

    queue = InMemoryJobQueue()

    scheduler = JobScheduler(
        queue=queue,
    )

    jobs = [
        CrawlJob(
            source=Source.FINELIB,
            listing_url="https://example.com/1",
            state="Lagos",
            city="Yaba",
            category_slug="restaurants",
        ),
        CrawlJob(
            source=Source.FINELIB,
            listing_url="https://example.com/2",
            state="Lagos",
            city="Lekki",
            category_slug="banks",
        ),
    ]

    await scheduler.schedule(
        jobs,
    )

    assert await queue.size() == 2

    first = await queue.dequeue()
    second = await queue.dequeue()

    assert first is not None
    assert second is not None

    assert first.city == "Yaba"
    assert second.city == "Lekki"

    assert await queue.is_empty()
