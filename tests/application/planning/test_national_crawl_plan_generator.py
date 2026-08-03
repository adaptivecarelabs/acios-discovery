from acios_discovery.application.planning import (
    CrawlPlanGenerator,
    NationalCrawlPlanGenerator,
)
from acios_discovery.application.planning.providers.category_provider import (
    CategoryProvider,
)
from acios_discovery.application.planning.providers.city_provider import (
    CityProvider,
)
from acios_discovery.application.planning.providers.state_provider import (
    StateProvider,
)


def test_generates_plans_for_every_state():

    generator = CrawlPlanGenerator(
        city_provider=CityProvider(),
        category_provider=CategoryProvider(),
    )

    national = NationalCrawlPlanGenerator(
        state_provider=StateProvider(),
        generator=generator,
    )

    plans = national.generate_all()

    assert len(plans) > 1000

    states = StateProvider().get_states()

    generated_states = {
        plan.state
        for plan in plans
    }

    assert set(states).issubset(generated_states)
