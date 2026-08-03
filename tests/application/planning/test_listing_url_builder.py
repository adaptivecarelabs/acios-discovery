from acios_discovery.application.planning.builders.listing_url_builder import (
    ListingUrlBuilder,
)
from acios_discovery.application.planning.models import (
    CrawlPlan,
)
from acios_discovery.application.planning.providers.category_provider import (
    CategoryProvider,
)


def test_build_food_url():

    builder = ListingUrlBuilder(
        CategoryProvider()
    )

    listing = builder.build(

        CrawlPlan(
            state="Lagos",
            city="Lagos",
            category_slug="food",
        )
    )

    assert listing.url.endswith(
        "/cities/lagos/food"
    )


def test_build_restaurants_url():

    builder = ListingUrlBuilder(
        CategoryProvider()
    )

    listing = builder.build(

        CrawlPlan(
            state="Lagos",
            city="Lagos",
            category_slug="restaurants",
        )
    )

    assert listing.url.endswith(
        "/cities/lagos/business/food/restaurants"
    )


def test_build_second_page():

    builder = ListingUrlBuilder(
        CategoryProvider()
    )

    listing = builder.build(

        CrawlPlan(
            state="Lagos",
            city="Lagos",
            category_slug="restaurants",
            page=2,
        )
    )

    assert listing.url.endswith(
        "/cities/lagos/business/food/restaurants?page=2"
    )
