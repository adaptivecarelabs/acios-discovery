from unittest.mock import AsyncMock

import pytest

from acios_discovery.application.discovery.detail_enrichment_engine import (
    DetailEnrichmentEngine,
)
from acios_discovery.application.enrichment.finelib_enricher import (
    FinelibEnricher,
)
from acios_discovery.domain.discovery.context import (
    DiscoveryContext,
)
from acios_discovery.domain.discovery.models import (
    RawDiscovery,
)
from acios_discovery.domain.discovery.record import (
    DiscoveryRecord,
)
from acios_discovery.domain.discovery.repository import (
    DiscoveryRepository,
)
from acios_discovery.domain.sources import (
    Source,
)


def make_record() -> DiscoveryRecord:
    return DiscoveryRecord(
        context=DiscoveryContext(
            source=Source.FINELIB,
            state="Lagos",
            city="Yaba",
            category="restaurants",
            listing_url="https://example.com",
        ),
        company=RawDiscovery(
            source=Source.FINELIB,
            business_name="ABC Ltd",
            detail_url="https://example.com/company/abc",
        ),
    )


@pytest.mark.asyncio
async def test_engine_returns_record() -> None:
    enricher = AsyncMock(
        spec=FinelibEnricher,
    )

    repository = AsyncMock(
        spec=DiscoveryRepository,
    )

    engine = DetailEnrichmentEngine(
        enricher=enricher,
        repository=repository,
    )

    record = make_record()

    enricher.enrich.return_value = record

    result = await engine.enrich(
        record,
    )

    assert result is record

    enricher.enrich.assert_awaited_once_with(
        record,
    )

    repository.save.assert_awaited_once_with(
        record,
    )


@pytest.mark.asyncio
async def test_engine_downloads_detail_page() -> None:
    enricher = AsyncMock(
        spec=FinelibEnricher,
    )

    repository = AsyncMock(
        spec=DiscoveryRepository,
    )

    engine = DetailEnrichmentEngine(
        enricher=enricher,
        repository=repository,
    )

    record = make_record()

    enricher.enrich.return_value = record

    await engine.enrich(
        record,
    )

    enricher.enrich.assert_awaited_once_with(
        record,
    )

    repository.save.assert_awaited_once_with(
        record,
    )
