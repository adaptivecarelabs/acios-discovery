from __future__ import annotations

from acios_discovery.application.enrichment.finelib_enricher import (
    FinelibEnricher,
)
from acios_discovery.domain.discovery import DiscoveryRecord
from acios_discovery.domain.discovery.repository import DiscoveryRepository
from acios_discovery.shared.logging import logger


class DetailEnrichmentEngine:

    def __init__(
        self,
        *,
        enricher: FinelibEnricher,
        repository: DiscoveryRepository,
    ) -> None:

        self._enricher = enricher
        self._repository = repository

    async def enrich(
        self,
        record: DiscoveryRecord,
    ) -> DiscoveryRecord:

        logger.info(
            "Enriching %s",
            record.company.business_name,
        )

        enriched = await self._enricher.enrich(
            record,
        )

        await self._repository.save(
            enriched,
        )

        logger.info(
            "Finished enrichment for %s",
            enriched.company.business_name,
        )

        return enriched
