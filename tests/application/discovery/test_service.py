import pytest

from acios_discovery.application.discovery.service import (
    DiscoveryService,
)
from acios_discovery.domain.crawling.job import CrawlJob
from acios_discovery.infrastructure.persistence.in_memory_discovery_repository import (
    InMemoryDiscoveryRepository,
)
from tests.fakes.test_html_client import FakeHttpClient


class FakeConnector:

    def __init__(self, records):
        self.records = records

    async def crawl_listing(
        self,
        **kwargs,
    ):
        return self.records


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
        [sample_discovery_record],
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
        source="finelib",
        listing_url="https://example.com",
        state="Lagos",
        city="Lagos",
        category_slug="health",
    )

    result = await service.run(job)

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
        [sample_discovery_record],
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
        source="finelib",
        listing_url="https://example.com",
        state="Lagos",
        city="Lagos",
        category_slug="health",
    )

    result = await service.run(job)

    assert result.records_found == 1
    assert result.records_saved == 0
    assert result.duplicates == 1

    assert await repository.count() == 1


@pytest.mark.asyncio
async def test_service_handles_empty_listing():

    repository = InMemoryDiscoveryRepository()

    connector = FakeConnector([])

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
        source="finelib",
        listing_url="https://example.com",
        state="Lagos",
        city="Lagos",
        category_slug="health",
    )

    result = await service.run(job)

    assert result.records_found == 0
    assert result.records_saved == 0
    assert result.duplicates == 0

    assert await repository.count() == 0
