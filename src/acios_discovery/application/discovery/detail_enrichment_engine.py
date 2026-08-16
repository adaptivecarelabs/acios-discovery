from __future__ import annotations

from acios_discovery.application.enrichment.finelib_enricher import (
    FinelibEnricher,
)
from acios_discovery.domain.discovery.record import (
    DiscoveryRecord,
)
from acios_discovery.domain.discovery.repository import (
    DiscoveryRepository,
)


class DetailEnrichmentEngine:
    """
    Enriches a discovery record using its source-specific enricher
    and persists the enriched result.

    The engine is deliberately responsible only for enrichment
    orchestration. Company registration is handled later by the
    discovery processor.
    """

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
        """
        Download/enrich the discovery detail page and persist
        the resulting discovery record.
        """

        enriched_record = await self._enricher.enrich(
            record,
        )

        await self._repository.save(
            enriched_record,
        )

        return enriched_record
