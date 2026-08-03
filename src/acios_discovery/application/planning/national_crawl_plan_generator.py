from __future__ import annotations

from acios_discovery.application.planning.crawl_plan_generator import (
    CrawlPlanGenerator,
)
from acios_discovery.application.planning.models import (
    CrawlPlan,
)
from acios_discovery.application.planning.providers.state_provider import (
    StateProvider,
)


class NationalCrawlPlanGenerator:
    """
    Generates crawl plans for every Nigerian state.
    """

    def __init__(
        self,
        *,
        state_provider: StateProvider,
        generator: CrawlPlanGenerator,
    ) -> None:

        self._state_provider = state_provider
        self._generator = generator

    def generate_all(
        self,
    ) -> list[CrawlPlan]:

        plans: list[CrawlPlan] = []

        for state in self._state_provider.get_states():

            plans.extend(
                self._generator.generate(
                    state=state,
                )
            )

        return plans
