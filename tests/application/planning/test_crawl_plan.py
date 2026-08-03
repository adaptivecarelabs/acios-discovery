from acios_discovery.application.planning.models import (
    CrawlPlan,
)


def test_default_page():

    plan = CrawlPlan(
        state="Lagos",
        city="Ikeja",
        category_slug="restaurants",
    )

    assert plan.page == 1


def test_values_are_preserved():

    plan = CrawlPlan(
        state="Kaduna",
        city="Zaria",
        category_slug="schools",
        page=4,
    )

    assert plan.state == "Kaduna"

    assert plan.city == "Zaria"

    assert plan.category_slug == "schools"

    assert plan.page == 4
