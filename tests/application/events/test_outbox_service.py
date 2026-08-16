from unittest.mock import AsyncMock

from acios_discovery.application.events.outbox_service import (
    OutboxService,
)

from acios_discovery.application.events.outbox_repository import (
    OutboxRepository,
)
from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.events.job_completed_event import (
    JobCompletedEvent,
)
from acios_discovery.domain.sources import Source


async def test_outbox_service_records_event():
    repository = AsyncMock(
        spec=OutboxRepository,
    )

    service = OutboxService(
        repository,
    )

    job = CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.com",
        state="Lagos",
        city="Yaba",
        category_slug="restaurants",
    )

    event = JobCompletedEvent(
        job=job,
        pages_crawled=1,
        companies_discovered=2,
    )

    await service.record(
        event,
    )

    repository.add.assert_awaited_once()
