from acios_discovery.infrastructure.persistence.mappers.discovery_mapper import (
    DiscoveryMapper,
)


def test_discovery_mapper_round_trip(
    finelib_restaurants_fixture: str,
) -> None:
    from acios_discovery.infrastructure.connectors.finelib.connector import (
        FinelibConnector,
    )
    from acios_discovery.infrastructure.connectors.finelib.listing_mapper import (
        FinelibMapper,
    )
    from acios_discovery.infrastructure.connectors.finelib.listing_parser import (
        FinelibParser,
    )

    import asyncio

    connector = FinelibConnector(
        parser=FinelibParser(),
        mapper=FinelibMapper(),
    )

    records = asyncio.run(
        connector.crawl_listing(
            html=finelib_restaurants_fixture,
            listing_url=(
                "https://www.finelib.com/cities/lagos/"
                "business/food/restaurants"
            ),
            state="Lagos",
            city="Lagos",
            category_slug="restaurants",
        )
    )

    original = records[0]

    orm = DiscoveryMapper.to_orm(original)

    restored = DiscoveryMapper.to_domain(orm)

    assert restored.company.business_name == (
        original.company.business_name
    )

    assert restored.company.address == (
        original.company.address
    )

    assert restored.company.phone_numbers == (
        original.company.phone_numbers
    )

    assert restored.company.detail_url == (
        original.company.detail_url
    )

    assert restored.company.description == (
        original.company.description
    )

    assert restored.context.source == (
        original.context.source
    )

    assert restored.context.state == (
        original.context.state
    )

    assert restored.context.city == (
        original.context.city
    )

    assert restored.context.industry == (
        original.context.industry
    )

    assert restored.context.category == (
        original.context.category
    )

    assert restored.context.subcategory == (
        original.context.subcategory
    )

    assert restored.context.listing_url == (
        original.context.listing_url
    )
