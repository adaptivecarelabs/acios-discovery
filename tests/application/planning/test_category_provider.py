from acios_discovery.application.planning.providers.category_provider import (
    CategoryProvider,
)


def test_returns_categories():

    provider = CategoryProvider()

    categories = provider.categories()

    assert len(categories) > 150

    assert "food" in categories

    assert "restaurants" in categories

    assert "healthcare" in categories


def test_returns_taxonomy():

    provider = CategoryProvider()

    taxonomy = provider.taxonomy(
        "restaurants"
    )

    assert taxonomy.industry == "Food"

    assert taxonomy.category == "Food"

    assert taxonomy.subcategory == "Restaurants"


def test_unknown_category():

    provider = CategoryProvider()

    assert not provider.has_category(
        "does-not-exist"
    )

    assert provider.has_category(
        "restaurants"
    )
