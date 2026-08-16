from __future__ import annotations

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
from acios_discovery.domain.crawling import (
    CrawlJob,
)
from acios_discovery.domain.discovery.context import (
    DiscoveryContext,
)
from acios_discovery.domain.discovery.models import (
    RawDiscovery,
)
from acios_discovery.domain.discovery.record import (
    DiscoveryRecord,
)
from acios_discovery.domain.sources import (
    Source,
)


def make_record(
    name: str = "Drugstoc",
) -> DiscoveryRecord:
    return DiscoveryRecord(
        company=RawDiscovery(
            source=Source.FINELIB,
            business_name=name,
        ),
        context=DiscoveryContext(
            source=Source.FINELIB,
            state="Lagos",
            city="Ikeja",
            category="Healthcare",
            listing_url="https://example.com",
        ),
    )


class FakeCrawler:
    async def execute(
        self,
        job: CrawlJob,
    ) -> ListingCrawlResult:
        assert job is not None

        record = make_record()

        return ListingCrawlResult(
            pages_crawled=1,
            companies_discovered=1,
            records=[record],
        )


class FakeEnricher:
    def __init__(self) -> None:
        self.records: list[DiscoveryRecord] = []

    async def enrich(
        self,
        record: DiscoveryRecord,
    ) -> DiscoveryRecord:
        self.records.append(record)
        return record


class FakePersistence:
    def __init__(self) -> None:
        self.records: list[DiscoveryRecord] = []

    async def persist(
        self,
        record: DiscoveryRecord,
    ) -> None:
        self.records.append(record)


class FakeBatchProcessor:
    def __init__(self) -> None:
        self.discoveries: list = []

    async def process(
        self,
        discoveries,
    ):
        self.discoveries.extend(discoveries)
        return discoveries


@pytest.mark.asyncio
async def test_pipeline_executes_successfully() -> None:
    persistence = FakePersistence()

    pipeline = DiscoveryPipeline(
        crawler=FakeCrawler(),
        enricher=FakeEnricher(),
        persistence=persistence,
        processor=FakeBatchProcessor(),
    )

    job = CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.com",
        state="Lagos",
        city="Ikeja",
        category_slug="healthcare",
        page=1,
    )

    result = await pipeline.execute(
        job,
    )

    assert isinstance(
        result,
        DiscoveryRunResult,
    )

    assert result.records_found == 1
    assert result.records_saved == 1
    assert result.duplicates == 0
    assert result.pages_crawled == 1
    assert result.source == Source.FINELIB.value

    assert len(persistence.records) == 1

    assert (
        persistence.records[0]
        .company.business_name
        == "Drugstoc"
    )
