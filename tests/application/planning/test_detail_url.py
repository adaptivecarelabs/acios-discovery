from acios_discovery.application.planning.models import (
    DetailUrl,
)
from acios_discovery.domain.sources import Source


def test_detail_url_model():

    detail = DetailUrl(
        source=Source.FINELIB,
        url="https://example.com/company",
        state="Lagos",
        city="Yaba",
        category_slug="restaurants",
    )

    assert detail.source is Source.FINELIB

    assert detail.url == "https://example.com/company"

    assert detail.state == "Lagos"

    assert detail.city == "Yaba"

    assert detail.category_slug == "restaurants"
