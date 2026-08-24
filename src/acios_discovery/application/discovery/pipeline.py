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
from acios_discovery.domain.errors.crawl_errors import CrawlError
from acios_discovery.shared.logging import logger


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

        errors: list[str] = []

        for record in crawl_result.records:

            try:
                enriched = await self._enricher.enrich(
                    record,
                )

            except CrawlError as exc:

                logger.warning(
                    "Detail-page enrichment failed for %s "
                    "(%s) — registering with listing-page "
                    "data only: %s",
                    record.company.business_name,
                    record.company.detail_url,
                    exc,
                )

                errors.append(
                    f"Enrichment failed for "
                    f"{record.company.business_name} "
                    f"({record.company.detail_url}): {exc}"
                )

                enriched = record

            await self._persistence.persist(
                enriched,
            )

            enriched_records.append(enriched)

        await self._processor.process(
            enriched_records,
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
            records=enriched_records,
            errors=errors,
        )
