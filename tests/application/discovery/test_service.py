from dataclasses import replace

import pytest
from acios_discovery.domain.sources import Source
from acios_discovery.application.discovery.service import (
    DiscoveryService,
)
from acios_discovery.domain.crawling.job import CrawlJob
from acios_discovery.infrastructure.persistence.in_memory_discovery_repository import (
    InMemoryDiscoveryRepository,
)
from tests.fakes.test_html_client import FakeHttpClient


class FakeConnector:

    def __init__(
        self,
        records=None,
        *,
        pages=None,
        next_pages=None,
    ):
        self.records = records or []
        self.pages = pages or {}
        self.next_pages = next_pages or {}
        self.calls: list[str] = []

    async def crawl_listing(
        self,
        *,
        listing_url: str,
        **kwargs,
    ):
        self.calls.append(
            listing_url,
        )

        if self.pages:
            return self.pages.get(
                listing_url,
                [],
            )

        return self.records

    def next_page_url(
        self,
        html: str,
        current_url: str,
    ) -> str | None:

        return self.next_pages.get(
            html,
        )


class FakeEnricher:

    def __init__(self):
        self.calls = 0

    async def enrich(
        self,
        record,
    ):
        self.calls += 1
        return record


@pytest.mark.asyncio
async def test_service_saves_new_records(
    sample_discovery_record,
):

    repository = InMemoryDiscoveryRepository()

    connector = FakeConnector(
        records=[sample_discovery_record],
    )

    enricher = FakeEnricher()

    service = DiscoveryService(
        connector=connector,
        enricher=enricher,
        repository=repository,
        http=FakeHttpClient(
            {
                "https://example.com": "<html></html>",
            }
        ),
    )

    job = CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.com",
        state="Lagos",
        city="Lagos",
        category_slug="health",
    )

    result = await service.run(job)

    assert result.pages_crawled == 1
    assert result.records_found == 1
    assert result.records_saved == 1
    assert result.duplicates == 0

    assert await repository.count() == 1

    assert enricher.calls == 1


@pytest.mark.asyncio
async def test_service_skips_duplicates(
    sample_discovery_record,
):

    repository = InMemoryDiscoveryRepository()

    await repository.save(
        sample_discovery_record,
    )

    connector = FakeConnector(
        records=[sample_discovery_record],
    )

    enricher = FakeEnricher()

    service = DiscoveryService(
        connector=connector,
        enricher=enricher,
        repository=repository,
        http=FakeHttpClient(
            {
                "https://example.com": "<html></html>",
            }
        ),
    )

    job = CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.com",
        state="Lagos",
        city="Lagos",
        category_slug="health",
    )

    result = await service.run(job)

    assert result.pages_crawled == 1
    assert result.records_found == 1
    assert result.records_saved == 0
    assert result.duplicates == 1

    assert await repository.count() == 1


@pytest.mark.asyncio
async def test_service_handles_empty_listing():

    repository = InMemoryDiscoveryRepository()

    connector = FakeConnector()

    enricher = FakeEnricher()

    service = DiscoveryService(
        connector=connector,
        enricher=enricher,
        repository=repository,
        http=FakeHttpClient(
            {
                "https://example.com": "<html></html>",
            }
        ),
    )

    job = CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.com",
        state="Lagos",
        city="Lagos",
        category_slug="health",
    )

    result = await service.run(job)

    assert result.pages_crawled == 1
    assert result.records_found == 0
    assert result.records_saved == 0
    assert result.duplicates == 0

    assert await repository.count() == 0


@pytest.mark.asyncio
async def test_service_crawls_multiple_listing_pages(
    sample_discovery_record,
):
    """
    Service should continue crawling until
    next_page_url() returns None.
    """

    repository = InMemoryDiscoveryRepository()

    page1_record = sample_discovery_record

    page2_record = sample_discovery_record.model_copy(
        update={
            "company": replace(
                sample_discovery_record.company,
                business_name="Second Business",
                detail_url="https://example.com/company-2",
            )
        }
    )

    connector = FakeConnector(
        pages={
            "https://example.com/page-1": [
                page1_record,
            ],
            "https://example.com/page-2": [
                page2_record,
            ],
        },
        next_pages={
            "<page-1>": "https://example.com/page-2",
            "<page-2>": None,
        },
    )

    service = DiscoveryService(
        connector=connector,
        enricher=FakeEnricher(),
        repository=repository,
        http=FakeHttpClient(
            {
                "https://example.com/page-1": "<page-1>",
                "https://example.com/page-2": "<page-2>",
            }
        ),
    )

    job = CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.com/page-1",
        state="Lagos",
        city="Lagos",
        category_slug="health",
    )

    result = await service.run(job)

    assert result.pages_crawled == 2
    assert result.records_found == 2
    assert result.records_saved == 2
    assert result.duplicates == 0

    assert await repository.count() == 2


@pytest.mark.asyncio
async def test_service_does_not_revisit_same_page(
    sample_discovery_record,
):
    """
    Service should stop if the connector
    returns a page that has already
    been crawled.
    """

    repository = InMemoryDiscoveryRepository()

    connector = FakeConnector(
        pages={
            "https://example.com/page-1": [
                sample_discovery_record,
            ],
        },
        next_pages={
            "<page-1>": "https://example.com/page-1",
        },
    )

    service = DiscoveryService(
        connector=connector,
        enricher=FakeEnricher(),
        repository=repository,
        http=FakeHttpClient(
            {
                "https://example.com/page-1": "<page-1>",
            }
        ),
    )

    job = CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.com/page-1",
        state="Lagos",
        city="Lagos",
        category_slug="health",
    )

    result = await service.run(job)

    assert result.pages_crawled == 1
    assert result.records_found == 1
    assert result.records_saved == 1

    assert connector.calls == [
        "https://example.com/page-1",
    ]
