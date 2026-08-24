from __future__ import annotations

from acios_discovery.application.discovery.listing_crawl_result import (
    ListingCrawlResult,
)
from acios_discovery.application.discovery.listing_downloader import (
    ListingDownloader,
)
from acios_discovery.application.planning.builders.listing_url_builder import (
    ListingUrlBuilder,
)
from acios_discovery.application.planning.models import CrawlPlan
from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.errors.crawl_errors import ListingNotFoundError
from acios_discovery.infrastructure.connectors.finelib.connector import (
    FinelibConnector,
)
from acios_discovery.shared.logging import logger


class ListingCrawlEngine:
    """
    Executes one CrawlJob and discovers records from listing pages.

    This engine is deliberately responsible only for crawling.

    Persistence is handled by DiscoveryPipeline through
    DiscoveryPersistenceService.

    The engine therefore:
        1. Builds the initial listing URL.
        2. Downloads listing pages.
        3. Parses listing pages.
        4. Follows pagination.
        5. Returns discovered records.

    It does NOT persist records.
    """

    def __init__(
        self,
        *,
        downloader: ListingDownloader,
        connector: FinelibConnector,
        url_builder: ListingUrlBuilder,
    ) -> None:
        self._downloader = downloader
        self._connector = connector
        self._url_builder = url_builder

    async def execute(
        self,
        job: CrawlJob,
    ) -> ListingCrawlResult:
        plan = CrawlPlan(
            state=job.state,
            city=job.city,
            category_slug=job.category_slug,
            page=job.page,
        )

        initial_listing = self._url_builder.build(
            plan,
        )

        current_url: str | None = initial_listing.url

        pages = 0
        companies = 0

        all_records = []

        visited_urls: set[str] = set()

        while current_url is not None:
            if current_url in visited_urls:
                logger.warning(
                    "Pagination loop detected at %s",
                    current_url,
                )
                break

            visited_urls.add(current_url)

            logger.info(
                "Downloading listing page %s",
                current_url,
            )

            try:
                html = await self._downloader.download(
                    current_url,
                )

            except ListingNotFoundError:
                logger.info(
                    "No listing exists for %s (404) — "
                    "treating as zero results, not a failure.",
                    current_url,
                )
                break

            if self._connector.is_fallback_page(html):
                logger.info(
                    "No dedicated listing for %s (Finelib "
                    "served its generic nationwide fallback "
                    "page) — treating as zero results, not "
                    "a failure.",
                    current_url,
                )
                break

            records = await self._connector.crawl_listing(
                html=html,
                listing_url=current_url,
                state=job.state,
                city=job.city,
                category_slug=job.category_slug,
            )

            logger.info(
                "Discovered %d companies from %s",
                len(records),
                current_url,
            )

            all_records.extend(records)

            companies += len(records)
            pages += 1

            current_url = self._connector.next_page_url(
                html=html,
                current_url=current_url,
            )

        logger.info(
            "Listing crawl completed "
            "(%d pages, %d discoveries)",
            pages,
            companies,
        )

        return ListingCrawlResult(
            pages_crawled=pages,
            companies_discovered=companies,
            records=all_records,
        )
