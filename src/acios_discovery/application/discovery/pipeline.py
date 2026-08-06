from __future__ import annotations

from acios_discovery.application.discovery.detail_enrichment_engine import (
    DetailEnrichmentEngine,
)
from acios_discovery.application.discovery.discovery_batch_processor import (
    DiscoveryBatchProcessor,
)
from acios_discovery.application.discovery.listing_crawl_engine import (
    ListingCrawlEngine,
)
from acios_discovery.application.discovery.result import (
    DiscoveryRunResult,
)
from acios_discovery.application.planning.models import (
    CrawlPlan,
)


class DiscoveryPipeline:
    """
    Complete end-to-end discovery pipeline.

        Listing Crawl
              │
              ▼
        Detail Enrichment
              │
              ▼
        Company Registration
              │
              ▼
        Company Repository
    """

    def __init__(
        self,
        *,
        crawler: ListingCrawlEngine,
        enricher: DetailEnrichmentEngine,
        processor: DiscoveryBatchProcessor,
    ) -> None:

        self._crawler = crawler
        self._enricher = enricher
        self._processor = processor

    async def execute(
        self,
        plan: CrawlPlan,
    ) -> DiscoveryRunResult:

        crawl_result = await self._crawler.execute(
            plan,
        )

        enriched = []

        for record in crawl_result.records:

            enriched_record = await self._enricher.enrich(
                record,
            )

            enriched.append(
                enriched_record,
            )

        companies = await self._processor.process(
            [
                record.company
                for record in enriched
            ],
        )

        return DiscoveryRunResult(
            source=crawl_result.source,
            records_found=len(enriched),
            records_saved=len(companies),
            duplicates=max(
                0,
                len(enriched) - len(companies),
            ),
        )
