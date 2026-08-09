from acios_discovery.application.discovery.result import (
    DiscoveryRunResult,
)
from acios_discovery.application.enrichment.finelib_enricher import (
    FinelibEnricher,
)
from acios_discovery.domain.crawling.job import CrawlJob
from acios_discovery.domain.discovery import (
    DiscoveryRepository,
)
from acios_discovery.domain.http import HttpClient
from acios_discovery.infrastructure.connectors.finelib.connector import (
    FinelibConnector,
)


class DiscoveryService:
    """
    Complete discovery pipeline.

    Listing
        ↓
    Discovery
        ↓
    Enrichment
        ↓
    Deduplication
        ↓
    Save
    """

    def __init__(
        self,
        *,
        connector: FinelibConnector,
        enricher: FinelibEnricher,
        repository: DiscoveryRepository,
        http: HttpClient,
    ) -> None:

        self._connector = connector
        self._enricher = enricher
        self._repository = repository
        self._http = http

    async def run(
        self,
        job: CrawlJob,
    ) -> DiscoveryRunResult:

        saved = 0
        duplicates = 0
        records_found = 0

        current_url: str | None = job.listing_url
        visited_urls: set[str] = set()

        while current_url is not None:

            if current_url in visited_urls:
                break

            visited_urls.add(current_url)

            listing_html = await self._http.get(
                current_url,
            )

            discoveries = await self._connector.crawl_listing(
                html=listing_html,
                listing_url=current_url,
                state=job.state,
                city=job.city,
                category_slug=job.category_slug,
            )

            records_found += len(
                discoveries,
            )

            for record in discoveries:

                record = await self._enricher.enrich(
                    record,
                )

                if await self._repository.exists(
                    record,
                ):
                    duplicates += 1
                    continue

                await self._repository.save(
                    record,
                )

                saved += 1

            current_url = (
                self._connector.next_page_url(
                    listing_html,
                    current_url,
                )
            )

        return DiscoveryRunResult(
            source=job.source,
            records_found=records_found,
            records_saved=saved,
            duplicates=duplicates,
        )
