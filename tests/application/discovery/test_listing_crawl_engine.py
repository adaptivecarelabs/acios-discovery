from unittest.mock import AsyncMock, Mock

import pytest

from acios_discovery.application.discovery import (
    ListingCrawlEngine,
)
from acios_discovery.application.planning.builders.listing_url_builder import (
    ListingUrlBuilder,
)
from acios_discovery.application.planning.providers.category_provider import (
    CategoryProvider,
)
from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.discovery import (
    DiscoveryRecord,
)
from acios_discovery.domain.discovery.context import (
    DiscoveryContext,
)
from acios_discovery.domain.discovery.models import (
    RawDiscovery,
)
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.connectors.finelib.connector import (
    FinelibConnector,
)
from acios_discovery.infrastructure.connectors.finelib.url_slug_mapper import (
    FinelibUrlSlugMapper,
)


def make_record(
    *,
    name: str = "Test Company",
) -> DiscoveryRecord:

    return DiscoveryRecord(
        context=DiscoveryContext(
            source=Source.FINELIB,
            state="Lagos",
            city="Lagos",
            category="restaurants",
            listing_url=(
                "https://example.com/listing"
            ),
            page_number=1,
        ),
        company=RawDiscovery(
            source=Source.FINELIB,
            business_name=name,
            detail_url=(
                "https://example.com/company"
            ),
        ),
    )


def make_builder() -> ListingUrlBuilder:

    return ListingUrlBuilder(
        CategoryProvider(),
        FinelibUrlSlugMapper(),
    )


@pytest.mark.asyncio
async def test_engine_returns_result() -> None:

    downloader = AsyncMock()

    downloader.download.return_value = (
        "<html></html>"
    )

    connector = Mock(
        spec=FinelibConnector,
    )

    connector.crawl_listing = AsyncMock(
        return_value=[],
    )

    connector.next_page_url.return_value = None

    repository = Mock()
    repository.save = AsyncMock()

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
        repository=repository,
        url_builder=make_builder(),
    )

    result = await engine.execute(
        CrawlJob(
            source=Source.FINELIB,
            listing_url="https://example.com",
            state="Lagos",
            city="Lagos",
            category_slug="restaurants",
        )
    )

    assert result.pages_crawled == 1

    assert result.companies_discovered == 0

    assert (
        downloader.download.call_count
        == 1
    )

    assert (
        connector.crawl_listing.await_count
        == 1
    )

    assert (
        connector.next_page_url.call_count
        == 1
    )


@pytest.mark.asyncio
async def test_engine_saves_records() -> None:

    downloader = AsyncMock()

    downloader.download.return_value = (
        "<html></html>"
    )

    records = [
        make_record(
            name="Company 1",
        ),
        make_record(
            name="Company 2",
        ),
        make_record(
            name="Company 3",
        ),
    ]

    connector = Mock(
        spec=FinelibConnector,
    )

    connector.crawl_listing = AsyncMock(
        return_value=records,
    )

    connector.next_page_url.return_value = None

    repository = Mock()
    repository.save = AsyncMock()

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
        repository=repository,
        url_builder=make_builder(),
    )

    result = await engine.execute(
        CrawlJob(
            source=Source.FINELIB,
            listing_url="https://example.com",
            state="Lagos",
            city="Lagos",
            category_slug="restaurants",
        )
    )

    assert (
        repository.save.await_count
        == 3
    )

    assert (
        result.companies_discovered
        == 3
    )

    assert result.pages_crawled == 1


@pytest.mark.asyncio
async def test_engine_follows_connector_next_url() -> None:

    downloader = AsyncMock()

    downloader.download.side_effect = [
        "<page-1>",
        "<page-2>",
        "<page-3>",
    ]

    connector = Mock(
        spec=FinelibConnector,
    )

    connector.crawl_listing = AsyncMock(
        side_effect=[
            [
                make_record(
                    name="Company 1",
                ),
            ],
            [
                make_record(
                    name="Company 2",
                ),
            ],
            [
                make_record(
                    name="Company 3",
                ),
            ],
        ],
    )

    connector.next_page_url.side_effect = [
        "https://example.com/page-2",
        "https://example.com/page-3",
        None,
    ]

    repository = Mock()
    repository.save = AsyncMock()

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
        repository=repository,
        url_builder=make_builder(),
    )

    result = await engine.execute(
        CrawlJob(
            source=Source.FINELIB,
            listing_url="https://example.com",
            state="Lagos",
            city="Lagos",
            category_slug="restaurants",
        )
    )

    assert result.pages_crawled == 3

    assert result.companies_discovered == 3

    assert (
        downloader.download.call_count
        == 3
    )

    assert (
        repository.save.await_count
        == 3
    )

    assert (
        downloader.download.call_args_list[0]
        .args[0]
        .startswith(
            "https://www.finelib.com/"
        )
    )

    assert (
        downloader.download.call_args_list[1]
        .args[0]
        == "https://example.com/page-2"
    )

    assert (
        downloader.download.call_args_list[2]
        .args[0]
        == "https://example.com/page-3"
    )


@pytest.mark.asyncio
async def test_engine_passes_current_url_to_next_page_parser() -> None:

    downloader = AsyncMock()

    downloader.download.return_value = (
        "<html></html>"
    )

    connector = Mock(
        spec=FinelibConnector,
    )

    connector.crawl_listing = AsyncMock(
        return_value=[],
    )

    connector.next_page_url.return_value = None

    repository = Mock()
    repository.save = AsyncMock()

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
        repository=repository,
        url_builder=make_builder(),
    )

    await engine.execute(
       CrawlJob(
            source=Source.FINELIB,
            listing_url="https://example.com",
            state="Lagos",
            city="Lagos",
            category_slug="restaurants",
        )
    )

    connector.next_page_url.assert_called_once()

    call = connector.next_page_url.call_args

    assert call.kwargs["html"] == (
        "<html></html>"
    )

    assert call.kwargs["current_url"].startswith(
        "https://www.finelib.com/"
    )


@pytest.mark.asyncio
async def test_engine_stops_on_pagination_loop() -> None:

    downloader = AsyncMock()

    downloader.download.return_value = (
        "<html></html>"
    )

    connector = Mock(
        spec=FinelibConnector,
    )

    connector.crawl_listing = AsyncMock(
        return_value=[],
    )

    connector.next_page_url.return_value = (
        "https://example.com/page-2"
    )

    repository = Mock()
    repository.save = AsyncMock()

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
        repository=repository,
        url_builder=make_builder(),
    )

    result = await engine.execute(
        CrawlJob(
            source=Source.FINELIB,
            listing_url="https://example.com",
            state="Lagos",
            city="Lagos",
            category_slug="restaurants",
        )
    )

    assert result.pages_crawled == 2

    assert (
        downloader.download.call_count
        == 2
    )


@pytest.mark.asyncio
async def test_engine_starts_from_job_page() -> None:
    downloader = AsyncMock()

    downloader.download.return_value = (
        "<html></html>"
    )

    connector = Mock(
        spec=FinelibConnector,
    )

    connector.crawl_listing = AsyncMock(
        return_value=[],
    )

    connector.next_page_url.return_value = None

    repository = Mock()
    repository.save = AsyncMock()

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
        repository=repository,
        url_builder=make_builder(),
    )

    await engine.execute(
        CrawlJob(
            source=Source.FINELIB,
            listing_url="https://example.com",
            state="Lagos",
            city="Lagos",
            category_slug="restaurants",
            page=7,
        )
    )

    requested_url = (
        downloader.download.call_args.args[0]
    )

    assert requested_url.endswith(
        "/page-7"
    )
