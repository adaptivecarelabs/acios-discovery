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
from acios_discovery.application.planning.models import (
    CrawlPlan,
)
from acios_discovery.domain.discovery.repository import (
    DiscoveryRepository,
)
from acios_discovery.infrastructure.connectors.finelib.connector import (
    FinelibConnector,
)


class ListingCrawlEngine:
    """
    Downloads every page belonging to a listing,
    parses all companies,
    and persists them.
    """

    def __init__(
        self,
        *,
        downloader: ListingDownloader,
        connector: FinelibConnector,
        repository: DiscoveryRepository,
        url_builder: ListingUrlBuilder,
    ) -> None:

        self._downloader = downloader
        self._connector = connector
        self._repository = repository
        self._url_builder = url_builder

    async def execute(
        self,
        plan: CrawlPlan,
    ) -> ListingCrawlResult:

        page = plan.page

        pages = 0

        companies = 0

        while True:

            listing = self._url_builder.build(
                plan.model_copy(
                    update={
                        "page": page,
                    }
                )
            )

            html = await self._downloader.download(
                listing.url,
            )

            records = await self._connector.crawl_listing(
                html=html,
                listing_url=listing.url,
                state=listing.state,
                city=listing.city,
                category_slug=listing.taxonomy_slug,
            )

            for record in records:
                await self._repository.save(record)

            companies += len(
                records,
            )

            pages += 1

            if not self._connector.has_next_page(
                html,
            ):
                break

            page += 1

        return ListingCrawlResult(
            pages_crawled=pages,
            companies_discovered=companies,
        )
