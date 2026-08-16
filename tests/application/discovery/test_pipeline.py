from unittest.mock import AsyncMock, Mock

import pytest

from acios_discovery.application.discovery.listing_crawl_result import (
    ListingCrawlResult,
)
from acios_discovery.application.discovery.pipeline import (
    DiscoveryPipeline,
)
from acios_discovery.application.discovery.result import (
    DiscoveryRunResult,
)
from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.discovery.context import (
    DiscoveryContext,
)
from acios_discovery.domain.discovery.models import (
    RawDiscovery,
)
from acios_discovery.domain.discovery.record import (
    DiscoveryRecord,
)
from acios_discovery.domain.sources import Source


def make_record(
    name: str,
) -> DiscoveryRecord:
    return DiscoveryRecord(
        context=DiscoveryContext(
            source=Source.FINELIB,
            state="Lagos",
            city="Lagos",
            category="health",
            listing_url="https://example.com/health",
            page_number=1,
        ),
        company=RawDiscovery(
            source=Source.FINELIB,
            business_name=name,
            detail_url=(
                f"https://example.com/company/{name.lower()}"
            ),
        ),
    )


def make_job() -> CrawlJob:
    return CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.com/health",
        state="Lagos",
        city="Lagos",
        category_slug="health",
    )


class FakePersistence:
    def __init__(self) -> None:
        self.records = []

    async def persist(
        self,
        record,
    ) -> None:
        self.records.append(record)


@pytest.fixture
def persistence() -> FakePersistence:
    return FakePersistence()



@pytest.mark.asyncio
async def test_pipeline_executes_listing_crawl(
    persistence: FakePersistence,
) -> None:
    crawler = Mock()
    crawler.execute = AsyncMock(
        return_value=ListingCrawlResult(
            pages_crawled=1,
            companies_discovered=0,
            records=[],
        ),
    )

    enricher = Mock()
    enricher.enrich = AsyncMock()

    processor = Mock()
    processor.process = AsyncMock(
        return_value=[],
    )

    pipeline = DiscoveryPipeline(
        crawler=crawler,
        enricher=enricher,
        persistence=persistence,
        processor=processor,
    )

    job = make_job()

    result = await pipeline.execute(
        job,
    )

    crawler.execute.assert_awaited_once_with(
        job,
    )

    assert isinstance(
        result,
        DiscoveryRunResult,
    )


@pytest.mark.asyncio
async def test_pipeline_enriches_every_record(
    persistence: FakePersistence,
) -> None:
    records = [
        make_record("Company One"),
        make_record("Company Two"),
        make_record("Company Three"),
    ]

    crawler = Mock()
    crawler.execute = AsyncMock(
        return_value=ListingCrawlResult(
            pages_crawled=1,
            companies_discovered=3,
            records=records,
        ),
    )

    enricher = Mock()
    enricher.enrich = AsyncMock(
        side_effect=lambda record: record,
    )

    processor = Mock()
    processor.process = AsyncMock(
        return_value=[],
    )

    pipeline = DiscoveryPipeline(
        crawler=crawler,
        enricher=enricher,
        persistence=persistence,
        processor=processor,
    )

    await pipeline.execute(
        make_job(),
    )

    assert (
        enricher.enrich.await_count
        == 3
    )

    assert (
        enricher.enrich.await_args_list[0].args[0]
        is records[0]
    )

    assert (
        enricher.enrich.await_args_list[1].args[0]
        is records[1]
    )

    assert (
        enricher.enrich.await_args_list[2].args[0]
        is records[2]
    )


@pytest.mark.asyncio
async def test_pipeline_passes_enriched_companies_to_processor(
    persistence: FakePersistence,
) -> None:
    record_one = make_record("Company One")
    record_two = make_record("Company Two")

    enriched_one = make_record("Enriched Company One")
    enriched_two = make_record("Enriched Company Two")

    crawler = Mock()
    crawler.execute = AsyncMock(
        return_value=ListingCrawlResult(
            pages_crawled=2,
            companies_discovered=2,
            records=[
                record_one,
                record_two,
            ],
        ),
    )

    enricher = Mock()
    enricher.enrich = AsyncMock(
        side_effect=[
            enriched_one,
            enriched_two,
        ],
    )

    processor = Mock()
    processor.process = AsyncMock(
        return_value=[],
    )

    pipeline = DiscoveryPipeline(
        crawler=crawler,
        enricher=enricher,
        persistence=persistence,
        processor=processor,
    )

    await pipeline.execute(
        make_job(),
    )

    processor.process.assert_awaited_once_with(
        [
            enriched_one.company,
            enriched_two.company,
        ],
    )


@pytest.mark.asyncio
async def test_pipeline_returns_correct_statistics(
    persistence: FakePersistence,
) -> None:
    records = [
        make_record("Company One"),
        make_record("Company Two"),
        make_record("Company Three"),
    ]

    companies = [
        Mock(),
        Mock(),
    ]

    crawler = Mock()
    crawler.execute = AsyncMock(
        return_value=ListingCrawlResult(
            pages_crawled=2,
            companies_discovered=3,
            records=records,
        ),
    )

    enricher = Mock()
    enricher.enrich = AsyncMock(
        side_effect=lambda record: record,
    )

    processor = Mock()
    processor.process = AsyncMock(
        return_value=companies,
    )

    pipeline = DiscoveryPipeline(
        crawler=crawler,
        enricher=enricher,
        persistence=persistence,
        processor=processor,
    )

    result = await pipeline.execute(
        make_job(),
    )

    assert result.source == Source.FINELIB.value
    assert result.pages_crawled == 2
    assert result.records_found == 3
    assert result.records_saved == 3
    assert result.duplicates == 0
