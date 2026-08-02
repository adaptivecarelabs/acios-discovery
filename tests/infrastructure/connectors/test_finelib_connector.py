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
async def test_healthcare_connector_returns_records(
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

    print(first.company.business_name)
    print(first.company.address)
    print(first.context.industry)
    print(first.company.phone_numbers)
    print(first.company.website)
    print(first.company.email)
    print(first.context.listing_url)
    print(first.company.detail_url)
    print(first.company.description)
    print(first.context.category)
    print(first.context.subcategory)

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

    assert first.context.root == "business"

@pytest.mark.asyncio
async def test_food_connector_returns_records(
    finelib_food_fixture: str,
):
    connector = FinelibConnector(
        parser=FinelibParser(),
        mapper=FinelibMapper(),
    )

    records = await connector.crawl_listing(
        html=finelib_food_fixture,
        listing_url="https://www.finelib.com/cities/lagos/business/food",
        state="Lagos",
        city="Lagos",
        category_slug="food",
    )

    assert len(records) > 0


    first = records[0]

    print(first.company.business_name)
    print(first.company.address)
    print(first.context.industry)
    print(first.company.phone_numbers)
    print(first.company.website)
    print(first.company.email)
    print(first.context.listing_url)
    print(first.company.detail_url)
    print(first.company.description)
    print(first.context.category)
    print(first.context.subcategory)

    assert first.context.source == Source.FINELIB
    assert first.company.business_name == "Ekene Global Ventures Ltd"
    assert first.company.address == "14, Offin Road, Oke-arin Market, Balogun, Lagos Nigeria"
    assert (first.company.phone_numbers == ["0817 407 0726"])
    assert first.company.website is None
    assert first.company.detail_url == "https://www.finelib.com/listing/Ekene-Global-Ventures-Ltd/24448/"
    assert first.context.listing_url == "https://www.finelib.com/cities/lagos/business/food"
    assert all(r.context.industry == "Food" for r in records)
    assert first.context.root == "business"
    assert all(r.context.category == "Food" for r in records)

    assert all(r.context.subcategory is None for r in records)

@pytest.mark.asyncio
async def test_restaurants_connector_returns_records(
    finelib_restaurants_fixture: str,
) -> None:

    connector = FinelibConnector(
        parser=FinelibParser(),
        mapper=FinelibMapper(),
    )

    records = await connector.crawl_listing(
        html=finelib_restaurants_fixture,
        listing_url=(
            "https://www.finelib.com/cities/lagos/"
            "business/food/restaurants"
        ),
        state="Lagos",
        city="Lagos",
        category_slug="restaurants",
    )

    assert len(records) > 0

    first = records[0]

    print(first.company.business_name)
    print(first.company.address)
    print(first.context.industry)
    print(first.company.phone_numbers)
    print(first.company.website)
    print(first.company.email)
    print(first.context.listing_url)
    print(first.company.detail_url)
    print(first.company.description)
    print(first.context.category)
    print(first.context.subcategory)

    assert all(
        r.context.industry == "Food"
        for r in records
    )

    assert all(
        r.context.category == "Food"
        for r in records
    )

    assert all(
        r.context.subcategory == "Restaurants"
        for r in records
    )
    assert first.context.root == "business"
