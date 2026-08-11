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
from acios_discovery.domain.crawling import CrawlJob


class DiscoveryPipeline:
    """
    Complete discovery pipeline for one executable CrawlJob.

    Pipeline:

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
        job: CrawlJob,
    ) -> DiscoveryRunResult:
        crawl_result = await self._crawler.execute(
            job,
        )

        enriched_records = []

        for record in crawl_result.records:
            enriched_record = await self._enricher.enrich(
                record,
            )

            enriched_records.append(
                enriched_record,
            )

        companies = await self._processor.process(
            [
                record.company
                for record in enriched_records
            ],
        )

        return DiscoveryRunResult(
            source=crawl_result.source.value,
            pages_crawled=crawl_result.pages_crawled,
            records_found=len(enriched_records),
            records_saved=len(companies),
            duplicates=max(
                0,
                len(enriched_records) - len(companies),
            ),
        )
