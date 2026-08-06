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
from acios_discovery.domain.discovery.context import DiscoveryContext
from acios_discovery.domain.discovery.models import RawDiscovery
from acios_discovery.domain.discovery.record import DiscoveryRecord
from acios_discovery.domain.sources import Source


class FakeCrawler:

    async def execute(self, plan):

        record = DiscoveryRecord(
            company=RawDiscovery(
                source=Source.FINELIB,
                business_name="Drugstoc",
            ),
            context=DiscoveryContext(
                source=Source.FINELIB,
                state="Lagos",
                city="Ikeja",
                category="Healthcare",
                listing_url="https://example.com",
            ),
        )

        return ListingCrawlResult(
            pages_crawled=1,
            companies_discovered=1,
            records=[record],
        )


class FakeEnricher:

    async def enrich(self, record):
        return record


class FakeBatchProcessor:

    async def process(
        self,
        discoveries,
        *,
        starting_sequence=1,
    ):
        return discoveries


@pytest.mark.asyncio
async def test_pipeline_executes_successfully():

    pipeline = DiscoveryPipeline(
        crawler=FakeCrawler(),
        enricher=FakeEnricher(),
        processor=FakeBatchProcessor(),
    )

    result = await pipeline.execute(plan=None)

    assert isinstance(result, DiscoveryRunResult)

    assert result.records_found == 1

    assert result.records_saved == 1

    assert result.duplicates == 0

    assert result.source == Source.FINELIB.value
