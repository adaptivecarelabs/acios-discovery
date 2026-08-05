from __future__ import annotations

from acios_discovery.application.enrichment.finelib_enricher import (
    FinelibEnricher,
)
from acios_discovery.domain.discovery import DiscoveryRecord
from acios_discovery.domain.discovery.repository import DiscoveryRepository


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

        enriched = await self._enricher.enrich(
            record,
        )

        return enriched
