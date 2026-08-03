from acios_discovery.application.planning import (
    CrawlPlanGenerator,
)
from acios_discovery.application.planning.providers.category_provider import (
    CategoryProvider,
)
from acios_discovery.application.planning.providers.city_provider import (
    CityProvider,
)


def test_generator_creates_plans():

    generator = CrawlPlanGenerator(
        city_provider=CityProvider(),
        category_provider=CategoryProvider(),
    )

    plans = generator.generate(
        state="Lagos",
    )

    assert len(plans) > 100

    assert plans[0].state == "Lagos"

    assert plans[0].city

    assert plans[0].category_slug
