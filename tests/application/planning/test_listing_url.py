from acios_discovery.application.planning.models import (
    ListingUrl,
)
from acios_discovery.domain.sources import Source


def test_listing_url():

    listing = ListingUrl(
        source=Source.FINELIB,
        url="https://example.com",
        state="Lagos",
        city="Ikeja",
        taxonomy_slug="restaurants",
        page=3,
    )

    assert listing.source == Source.FINELIB

    assert listing.url == "https://example.com"

    assert listing.state == "Lagos"

    assert listing.city == "Ikeja"

    assert listing.taxonomy_slug == "restaurants"

    assert listing.page == 3
