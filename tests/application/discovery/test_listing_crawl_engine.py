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

    connector.is_fallback_page.return_value = False

    connector.crawl_listing = AsyncMock(
        return_value=[],
    )

    connector.next_page_url.return_value = None

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
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
async def test_engine_returns_discovered_records() -> None:

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

    connector.is_fallback_page.return_value = False

    connector.crawl_listing = AsyncMock(
        return_value=records,
    )

    connector.next_page_url.return_value = None

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
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
        result.companies_discovered
        == 3
    )
    assert result.records == records
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

    connector.is_fallback_page.return_value = False

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

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
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

    connector.is_fallback_page.return_value = False

    connector.crawl_listing = AsyncMock(
        return_value=[],
    )

    connector.next_page_url.return_value = None

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
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

    connector.is_fallback_page.return_value = False

    connector.crawl_listing = AsyncMock(
        return_value=[],
    )

    connector.next_page_url.return_value = (
        "https://example.com/page-2"
    )

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
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

    connector.is_fallback_page.return_value = False

    connector.crawl_listing = AsyncMock(
        return_value=[],
    )

    connector.next_page_url.return_value = None

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
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


@pytest.mark.asyncio
async def test_engine_returns_zero_results_on_404_without_raising() -> None:
    """
    Regression test: a 404 on a listing page (e.g. our slug
    mapping guessed the wrong category path for this city) must
    resolve as zero results, not propagate as a job failure.
    """

    from acios_discovery.domain.errors.crawl_errors import (
        ListingNotFoundError,
    )

    downloader = AsyncMock()

    downloader.download.side_effect = ListingNotFoundError(
        "simulated 404",
    )

    connector = Mock(
        spec=FinelibConnector,
    )

    connector.is_fallback_page.return_value = False

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
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

    assert result.pages_crawled == 0
    assert result.companies_discovered == 0
    assert result.records == []

    # crawl_listing must never be called — there was no real
    # page content to parse.
    connector.crawl_listing.assert_not_called()


@pytest.mark.asyncio
async def test_engine_skips_fallback_page_without_extracting_records() -> None:
    """
    Regression test for the Yaba/Lekki/Ikeja incident: Finelib
    serves a generic nationwide fallback page (HTTP 200) for
    (city, category) combinations with no dedicated listing.
    The engine must detect this and treat it as zero results,
    never parsing the fallback page's (unrelated, shared-across-
    every-invalid-city) business cards as if they were real
    results for this city.
    """

    downloader = AsyncMock()

    downloader.download.return_value = (
        "<html><h1>Nigeria Health Sectors</h1></html>"
    )

    connector = Mock(
        spec=FinelibConnector,
    )

    connector.is_fallback_page.return_value = True

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
        url_builder=make_builder(),
    )

    result = await engine.execute(
        CrawlJob(
            source=Source.FINELIB,
            listing_url="https://example.com",
            state="Lagos",
            city="Lagos",
            category_slug="healthcare",
        )
    )

    assert result.pages_crawled == 0
    assert result.companies_discovered == 0
    assert result.records == []

    connector.crawl_listing.assert_not_called()


@pytest.mark.asyncio
async def test_engine_proceeds_normally_when_not_fallback_and_not_404() -> None:
    """
    Sanity check that the new checks don't interfere with the
    normal, successful path — a real listing page still gets
    parsed as before.
    """

    downloader = AsyncMock()

    downloader.download.return_value = (
        "<html><h1>Lagos Restaurants</h1></html>"
    )

    connector = Mock(
        spec=FinelibConnector,
    )

    connector.is_fallback_page.return_value = False

    connector.crawl_listing = AsyncMock(
        return_value=[make_record(name="Real Company")],
    )

    connector.next_page_url.return_value = None

    engine = ListingCrawlEngine(
        downloader=downloader,
        connector=connector,
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
    assert result.companies_discovered == 1
    connector.crawl_listing.assert_called_once()
