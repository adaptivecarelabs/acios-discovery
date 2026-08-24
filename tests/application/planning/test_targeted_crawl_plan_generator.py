import pytest

from acios_discovery.application.planning.providers.category_provider import (
    CategoryProvider,
)
from acios_discovery.application.planning.providers.city_provider import (
    CityProvider,
)
from acios_discovery.application.planning.targeted_crawl_plan_generator import (
    TargetedCrawlPlanGenerator,
)


def build_generator() -> TargetedCrawlPlanGenerator:
    return TargetedCrawlPlanGenerator(
        city_provider=CityProvider(),
        category_provider=CategoryProvider(),
    )


def test_generates_targeted_plan() -> None:
    generator = build_generator()

    plan = generator.generate(
        state="Lagos",
        city="Ikeja",
        category_slug="restaurants",
    )

    assert plan.state == "Lagos"
    assert plan.city == "Ikeja"
    assert plan.category_slug == "restaurants"
    assert plan.page == 1


def test_rejects_unknown_city() -> None:
    generator = build_generator()

    with pytest.raises(ValueError, match="Unknown city"):
        generator.generate(
            state="Lagos",
            city="DefinitelyNotACity",
            category_slug="restaurants",
        )


def test_rejects_unknown_category() -> None:
    generator = build_generator()

    with pytest.raises(ValueError):
        generator.generate(
            state="Lagos",
            city="Ikeja",
            category_slug="definitely-not-a-category",
        )
