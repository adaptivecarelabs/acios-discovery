from __future__ import annotations

from acios_discovery.application.discovery.detail_enrichment_engine import (
    DetailEnrichmentEngine,
)
from acios_discovery.domain.events.company_discovered_event import (
    CompanyDiscoveredEvent,
)


class DetailEnrichmentSubscriber:
    """
    Receives CompanyDiscoveredEvent and
    delegates enrichment to the
    DetailEnrichmentEngine.
    """

    def __init__(
        self,
        engine: DetailEnrichmentEngine,
    ) -> None:
        self._engine = engine

    async def __call__(
        self,
        event: CompanyDiscoveredEvent,
    ) -> None:

        await self._engine.enrich(
            event.record,
        )
