import pytest

from acios_discovery.domain.crawling.job import CrawlJob
from acios_discovery.infrastructure.queue.in_memory_job_queue import (
    InMemoryJobQueue,
)


@pytest.mark.asyncio
async def test_enqueue_adds_job() -> None:

    queue = InMemoryJobQueue()

    job = CrawlJob(
        source="finelib",
        listing_url="https://example.com",
        state="Lagos",
        city="Lagos",
        category_slug="health",
    )

    await queue.enqueue(job)

    assert await queue.size() == 1


@pytest.mark.asyncio
async def test_dequeue_returns_job() -> None:

    queue = InMemoryJobQueue()

    job = CrawlJob(
        source="finelib",
        listing_url="https://example.com",
        state="Lagos",
        city="Lagos",
        category_slug="health",
    )

    await queue.enqueue(job)

    result = await queue.dequeue()

    assert result == job
    assert await queue.size() == 0


@pytest.mark.asyncio
async def test_dequeue_empty_returns_none() -> None:

    queue = InMemoryJobQueue()

    assert await queue.dequeue() is None
