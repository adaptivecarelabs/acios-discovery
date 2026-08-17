from __future__ import annotations

from acios_discovery.application.planning.models import (
    CrawlPlan,
)
from acios_discovery.application.planning.providers.category_provider import (
    CategoryProvider,
)
from acios_discovery.application.planning.providers.city_provider import (
    CityProvider,
)


class TargetedCrawlPlanGenerator:
    """
    Generates one crawl plan for an explicitly requested
    state, city, and category.
    """

    def __init__(
        self,
        city_provider: CityProvider,
        category_provider: CategoryProvider,
    ) -> None:
        self._city_provider = city_provider
        self._category_provider = category_provider

    def generate(
        self,
        *,
        state: str,
        city: str,
        category_slug: str,
    ) -> CrawlPlan:
        cities = self._city_provider.get_cities(
            state,
        )

        if city not in cities:
            raise ValueError(
                f"Unknown city '{city}' for state '{state}'."
            )

        self._category_provider.require(
            category_slug,
        )

        return CrawlPlan(
            state=state,
            city=city,
            category_slug=category_slug,
        )
