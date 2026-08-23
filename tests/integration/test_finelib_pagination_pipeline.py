from __future__ import annotations

from collections.abc import Mapping

import pytest

from acios_discovery.application.discovery.listing_crawl_engine import (
    ListingCrawlEngine,
)
from acios_discovery.application.discovery.listing_downloader import (
    ListingDownloader,
)
from acios_discovery.application.planning.models import CrawlPlan, ListingUrl
from acios_discovery.domain.crawling.job import CrawlJob
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.connectors.finelib.connector import (
    FinelibConnector,
)
from acios_discovery.infrastructure.connectors.finelib.listing_mapper import (
    FinelibMapper,
)
from acios_discovery.infrastructure.connectors.finelib.listing_parser import (
    FinelibParser,
)

PAGE_1_URL = "https://www.finelib.com/cities/lagos/agriculture"
PAGE_2_URL = "https://www.finelib.com/cities/lagos/agriculture/page-2"


class FixtureHttpClient:
    """
    Fake HTTP client backed by real HTML fixtures.

    Records every requested URL so the test can verify exactly
    which listing pages were downloaded, and in what order.
    """

    def __init__(
        self,
        pages: Mapping[str, str],
    ) -> None:
        self._pages = dict(pages)
        self.requests: list[str] = []

    async def get(
        self,
        url: str,
    ) -> str:
        self.requests.append(url)
        return self._pages[url]


class FixedListingUrlBuilder:
    """
    Returns PAGE_1_URL for every plan, regardless of category_slug.

    Real taxonomy/slug resolution has its own tests; this test is
    only concerned with whether ListingCrawlEngine correctly
    follows pagination once given a starting URL.
    """

    def build(
        self,
        plan: CrawlPlan,
    ) -> ListingUrl:
        return ListingUrl(
            source=Source.FINELIB,
            url=PAGE_1_URL,
            state=plan.state,
            city=plan.city,
            taxonomy_slug=plan.category_slug,
            page=plan.page,
        )


def _count_records_from_page(html: str) -> int:
    """
    Independently count business cards on a fixture page using
    the same parser method the connector relies on, so the test
    doesn't hardcode a fixture-specific magic number that would
    silently go stale if the fixture is ever regenerated.
    """

    parser = FinelibParser()

    return len(
        parser.find_business_cards(html),
    )


@pytest.mark.asyncio
async def test_listing_crawl_engine_follows_pagination_across_real_pages(
    lagos_agriculture_service_page1: str,
    lagos_agriculture_service_page2: str,
) -> None:
    """
    Regression coverage for multi-page listing crawls.

    This replaces the pre-consolidation
    test_real_connector_crawls_multiple_pages, which exercised the
    same behavior through the now-removed DiscoveryService /
    InMemoryDiscoveryRepository classes. ListingCrawlEngine is the
    current architecture's equivalent responsibility: download a
    listing page, follow FinelibParser.next_page_url() until it
    returns None, and aggregate records across every page crawled.
    """

    http = FixtureHttpClient(
        {
            PAGE_1_URL: lagos_agriculture_service_page1,
            PAGE_2_URL: lagos_agriculture_service_page2,
        }
    )

    engine = ListingCrawlEngine(
        downloader=ListingDownloader(client=http),
        connector=FinelibConnector(
            parser=FinelibParser(),
            mapper=FinelibMapper(),
        ),
        url_builder=FixedListingUrlBuilder(),
    )

    job = CrawlJob(
        source=Source.FINELIB,
        listing_url=PAGE_1_URL,
        state="Lagos",
        city="Lagos",
        category_slug="healthcare",
    )

    result = await engine.execute(job)

    # Both listing pages were downloaded, in order, exactly once
    # each — proving pagination was followed and the loop
    # terminated correctly on page 2 (next_page_url returns None).
    assert http.requests == [PAGE_1_URL, PAGE_2_URL]

    assert result.pages_crawled == 2

    assert result.companies_discovered > 0

    assert len(result.records) == result.companies_discovered

    # Records genuinely came from both pages, not just page 1 —
    # guards against a bug where pagination "runs" (both pages
    # downloaded) but page 2's records are silently discarded.
    page_1_only_count = _count_records_from_page(
        lagos_agriculture_service_page1,
    )

    assert result.companies_discovered > page_1_only_count
