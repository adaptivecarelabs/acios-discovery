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


class CrawlPlanGenerator:
    """
    Generates crawl plans for a state.
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
    ) -> list[CrawlPlan]:

        plans: list[CrawlPlan] = []

        cities = self._city_provider.get_cities(
            state,
        )

        categories = (
            self._category_provider.categories()
        )

        for city in cities:

            for category in categories:

                plans.append(
                    CrawlPlan(
                        state=state,
                        city=city,
                        category_slug=category,
                    )
                )

        return plans
