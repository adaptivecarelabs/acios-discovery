from __future__ import annotations

from acios_discovery.application.planning.filtered_crawl_plan_generator import (
    FilteredCrawlPlanGenerator,
)
from acios_discovery.application.planning.models import CrawlPlan


class FakeInnerGenerator:
    def __init__(self, plans: list[CrawlPlan]) -> None:
        self._plans = plans

    def generate(self, *, state: str) -> list[CrawlPlan]:
        return self._plans


def make_plans() -> list[CrawlPlan]:
    return [
        CrawlPlan(state="Lagos", city="Lagos", category_slug="healthcare"),
        CrawlPlan(state="Lagos", city="Lagos", category_slug="restaurants"),
        CrawlPlan(state="Lagos", city="Ikeja", category_slug="healthcare"),
        CrawlPlan(state="Lagos", city="Ikeja", category_slug="restaurants"),
    ]


def test_no_filters_returns_everything_unchanged():
    inner = FakeInnerGenerator(make_plans())
    generator = FilteredCrawlPlanGenerator(inner=inner)

    result = generator.generate(state="Lagos")

    assert len(result) == 4


def test_category_filter_narrows_to_matching_categories_only():
    inner = FakeInnerGenerator(make_plans())
    generator = FilteredCrawlPlanGenerator(
        inner=inner,
        categories=["healthcare"],
    )

    result = generator.generate(state="Lagos")

    assert len(result) == 2
    assert all(p.category_slug == "healthcare" for p in result)


def test_max_jobs_caps_total_count():
    inner = FakeInnerGenerator(make_plans())
    generator = FilteredCrawlPlanGenerator(
        inner=inner,
        max_jobs=2,
    )

    result = generator.generate(state="Lagos")

    assert len(result) == 2


def test_category_filter_and_max_jobs_combine():
    inner = FakeInnerGenerator(make_plans())
    generator = FilteredCrawlPlanGenerator(
        inner=inner,
        categories=["healthcare", "restaurants"],
        max_jobs=1,
    )

    result = generator.generate(state="Lagos")

    assert len(result) == 1


def test_empty_category_set_returns_no_plans():
    inner = FakeInnerGenerator(make_plans())
    generator = FilteredCrawlPlanGenerator(
        inner=inner,
        categories=[],
    )

    # An explicitly empty (but non-None) list should still be
    # treated as "no categories requested" -> zero plans, not
    # "no filter applied".
    result = generator.generate(state="Lagos")

    assert result == []
