from __future__ import annotations


class FinelibUrlSlugMapper:
    """
    Maps canonical taxonomy slugs to Finelib listing URL paths.

    The returned value is the complete category path relative to
    /cities/{city}/, not merely the final URL segment.

    Examples:
        healthcare -> health
        food       -> business/food
        restaurants -> business/food/restaurants
        agriculture -> agriculture
    """

    _OVERRIDES: dict[str, str] = {
        "healthcare": "health",
        "food": "business/food",
        "restaurants": "business/food/restaurants",
    }

    def listing_path(
        self,
        taxonomy_slug: str,
    ) -> str:
        return self._OVERRIDES.get(
            taxonomy_slug,
            taxonomy_slug,
        )
