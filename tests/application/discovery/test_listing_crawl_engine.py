from unittest.mock import AsyncMock, Mock

import pytest

from acios_discovery.application.discovery import (
    ListingCrawlEngine,
)
from acios_discovery.application.planning.builders.listing_url_builder import (
    ListingUrlBuilder,
)
from acios_discovery.application.planning.models import (
    CrawlPlan,
)
from acios_discovery.application.planning.providers.category_provider import (
    CategoryProvider,
)
from acios_discovery.domain.discovery import (
    DiscoveryRecord,
)
from acios_discovery.domain.discovery.context import (
    DiscoveryContext,
)
from acios_discovery.domain.discovery.models import (
    RawDiscovery,
)
from acios_discovery.domain.repositories.discovery_repository import (
    DiscoveryRepository,
)
from acios_discovery.infrastructure.connectors.finelib.connector import (
    FinelibConnector,
)
from acios_discovery.infrastructure.persistence.in_memory_discovery_repository import (
    InMemoryDiscoveryRepository,
)

repository = AsyncMock(spec=DiscoveryRepository)



def make_record(
    *,
    name: str = "Test Company",
) -> DiscoveryRecord:

    return DiscoveryRecord(
        context=DiscoveryContext(
            source="finelib",
            state="Lagos",
            city="Lagos",
            category="restaurants",
            listing_url="https://example.com/listing",
            page_number=1,
        ),
        company=RawDiscovery(
            source="finelib",
            business_name=name,
            detail_url="https://example.com/company",
        ),
    )

@pytest.mark.asyncio
async def test_engine_returns_result():

    downloader = AsyncMock()

    downloader.download.return_value = "<html></html>"

    connector = Mock(spec=FinelibConnector)

    connector.crawl_listing = AsyncMock(
        return_value=[],
    )

    connector.has_next_page.return_value = False

    repository = Mock(
        spec=InMemoryDiscoveryRepository,
    )

    builder = ListingUrlBuilder(
        CategoryProvider(),
    )

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
        repository=repository,
        url_builder=builder,
    )

    result = await engine.execute(

        CrawlPlan(
            state="Lagos",
            city="Lagos",
            category_slug="restaurants",
        )
    )

    assert result.pages_crawled == 1

    assert result.companies_discovered == 0


@pytest.mark.asyncio
async def test_engine_saves_records():

    downloader = AsyncMock()

    downloader.download.return_value = "<html></html>"

    record = make_record()

    connector = Mock(spec=FinelibConnector)

    connector.crawl_listing = AsyncMock(
        return_value=[
            record,
            record,
            record,
        ]
    )

    connector.has_next_page.return_value = False

    repository = Mock()
    repository.save = AsyncMock()

    builder = ListingUrlBuilder(
        CategoryProvider(),
    )

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
        repository=repository,
        url_builder=builder,
    )

    result = await engine.execute(

        CrawlPlan(
            state="Lagos",
            city="Lagos",
            category_slug="restaurants",
        )
    )

    assert repository.save.await_count == 3

    assert result.companies_discovered == 3


@pytest.mark.asyncio
async def test_engine_handles_multiple_pages():

    downloader = AsyncMock()

    downloader.download.return_value = "<html></html>"

    connector = Mock(spec=FinelibConnector)

    connector.crawl_listing = AsyncMock(
        side_effect=[
            [
                make_record(name="Company 1"),
            ],
            [
                make_record(name="Company 2"),
                make_record(name="Company 3"),
            ],
        ]
    )

    connector.has_next_page.side_effect = [
        True,
        False,
    ]

    repository = Mock()
    repository.save = AsyncMock()

    builder = ListingUrlBuilder(
        CategoryProvider(),
    )

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
        repository=repository,
        url_builder=builder,
    )

    result = await engine.execute(

        CrawlPlan(
            state="Lagos",
            city="Lagos",
            category_slug="restaurants",
        )
    )

    assert downloader.download.call_count == 2

    assert repository.save.await_count == 3

    assert result.pages_crawled == 2

    assert result.companies_discovered == 3
