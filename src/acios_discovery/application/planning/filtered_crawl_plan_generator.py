from __future__ import annotations

from collections.abc import Iterable

from acios_discovery.application.planning.models import CrawlPlan


class FilteredCrawlPlanGenerator:
    """
    Wraps another plan generator, optionally narrowing its
    output to a set of categories and/or capping the total
    number of plans returned.

    Matches the same generate(*, state) -> list[CrawlPlan]
    shape every other planner in this codebase uses
    (CrawlPlanGenerator, TwoPlanGenerator, FixedPlanner, etc.),
    so it can be dropped in as the `planner=` argument to
    DiscoveryServices without any other code needing to change.
    """

    def __init__(
        self,
        *,
        inner,
        categories: Iterable[str] | None = None,
        max_jobs: int | None = None,
    ) -> None:
        self._inner = inner
        self._categories = (
            set(categories) if categories is not None else None
        )
        self._max_jobs = max_jobs

    def generate(
        self,
        *,
        state: str,
    ) -> list[CrawlPlan]:

        plans = self._inner.generate(state=state)

        if self._categories is not None:
            plans = [
                plan
                for plan in plans
                if plan.category_slug in self._categories
            ]

        if self._max_jobs is not None:
            plans = plans[: self._max_jobs]

        return plans
