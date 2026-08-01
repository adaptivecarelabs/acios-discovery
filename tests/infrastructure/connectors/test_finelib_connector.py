import pytest

from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.connectors.finelib.connector import (
    FinelibConnector,
)
from acios_discovery.infrastructure.connectors.finelib.mapper import (
    FinelibMapper,
)
from acios_discovery.infrastructure.connectors.finelib.parser import (
    FinelibParser,
)


@pytest.mark.asyncio
async def test_connector_returns_discovery_records(
    finelib_health_fixture: str,
) -> None:

    connector = FinelibConnector(
        parser=FinelibParser(),
        mapper=FinelibMapper(),
    )

    records = await connector.crawl_listing(
        html=finelib_health_fixture,
        listing_url="https://www.finelib.com/cities/lagos/health",
        state="Lagos",
        city="Lagos",
        category_slug="healthcare",
    )

    assert len(records) == 23

    first = records[0]

    assert (
        first.company.business_name
        == "Phytoscience Double Stem Cell"
    )

    assert (
        first.company.address
        == "No. 23 Opebi Road, Opebi- Ikeja, Lagos"
    )

    assert len(
        first.company.phone_numbers
    ) == 3

    assert (
        first.context.source
        == Source.FINELIB
    )

    assert (
        first.context.industry
        == "Healthcare"
    )

    assert (
        first.context.category
        == "Healthcare"
    )

    assert (
        first.context.listing_url
        == "https://www.finelib.com/cities/lagos/health"
    )
