from unittest.mock import AsyncMock

import pytest

from acios_discovery.application.discovery.detail_enrichment_engine import (
    DetailEnrichmentEngine,
)
from acios_discovery.application.events.in_memory_event_publisher import (
    InMemoryEventPublisher,
)
from acios_discovery.application.subscribers.detail_enrichment_subscriber import (
    DetailEnrichmentSubscriber,
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
from acios_discovery.domain.events.company_discovered_event import (
    CompanyDiscoveredEvent,
)
from acios_discovery.domain.sources import Source


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
async def test_subscriber_enriches_company():

    engine = AsyncMock(
        spec=DetailEnrichmentEngine,
    )

    subscriber = DetailEnrichmentSubscriber(
        engine,
    )

    publisher = InMemoryEventPublisher()

    publisher.subscribe(
        subscriber,
    )

    record = make_record()

    await publisher.publish(
        CompanyDiscoveredEvent(
            record=record,
        )
    )

    engine.enrich.assert_awaited_once_with(
        record,
    )
