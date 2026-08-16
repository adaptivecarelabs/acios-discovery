from __future__ import annotations

from acios_discovery.application.discovery.detail_enrichment_engine import (
    DetailEnrichmentEngine,
)
from acios_discovery.application.discovery.discovery_batch_processor import (
    DiscoveryBatchProcessor,
)
from acios_discovery.application.discovery.discovery_persistence_service import (
    DiscoveryPersistenceService,
)
from acios_discovery.application.discovery.listing_crawl_engine import (
    ListingCrawlEngine,
)
from acios_discovery.application.discovery.listing_crawl_result import (
    ListingCrawlResult,
)
from acios_discovery.application.discovery.result import (
    DiscoveryRunResult,
)
from acios_discovery.domain.crawling import CrawlJob


class DiscoveryPipeline:
    """
    Authoritative application-level discovery execution pipeline.

    The pipeline coordinates the complete discovery lifecycle:

        Crawl
          ↓
        Enrich
          ↓
        Persist discovery + outbox event
          ↓
        Register company

    Individual engines remain focused on one responsibility.
    """

    def __init__(
        self,
        *,
        crawler: ListingCrawlEngine,
        enricher: DetailEnrichmentEngine,
        persistence: DiscoveryPersistenceService,
        processor: DiscoveryBatchProcessor,
    ) -> None:
        self._crawler = crawler
        self._enricher = enricher
        self._persistence = persistence
        self._processor = processor

    async def execute(
        self,
        job: CrawlJob,
    ) -> DiscoveryRunResult:
        crawl_result: ListingCrawlResult = (
            await self._crawler.execute(
                job,
            )
        )

        enriched_records = []

        for record in crawl_result.records:
            enriched = await self._enricher.enrich(
                record,
            )

            await self._persistence.persist(
                enriched,
            )

            enriched_records.append(enriched)

        discoveries = [
            record.company
            for record in enriched_records
        ]

        await self._processor.process(
            discoveries,
        )

        return DiscoveryRunResult(
            records_found=len(
                crawl_result.records,
            ),
            records_saved=len(
                enriched_records,
            ),
            duplicates=0,
            pages_crawled=(
                crawl_result.pages_crawled
            ),
            source=job.source.value,
        )
