import pytest

from acios_discovery.application.crawling.crawl_job_factory import (
    CrawlJobFactory,
)
from acios_discovery.application.crawling.crawl_plan_submission_service import (
    CrawlPlanSubmissionService,
)
from acios_discovery.application.crawling.job_scheduler import (
    JobScheduler,
)
from acios_discovery.application.planning.builders.listing_url_builder import (
    ListingUrlBuilder,
)
from acios_discovery.application.planning.models import (
    CrawlPlan,
)
from acios_discovery.application.planning.providers.category_provider import (
    CategoryProvider,
)
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.connectors.finelib.url_slug_mapper import (
    FinelibUrlSlugMapper,
)
from acios_discovery.infrastructure.queue.in_memory_job_queue import (
    InMemoryJobQueue,
)


@pytest.mark.asyncio
async def test_submits_plans_as_jobs() -> None:

    queue = InMemoryJobQueue()

    scheduler = JobScheduler(
        queue=queue,
    )

    listing_builder = ListingUrlBuilder(
        taxonomy=CategoryProvider(),
        slug_mapper=FinelibUrlSlugMapper(),
    )

    service = CrawlPlanSubmissionService(
        listing_builder=listing_builder,
        job_factory=CrawlJobFactory(),
        scheduler=scheduler,
    )

    plans = [
        CrawlPlan(
            state="Lagos",
            city="Yaba",
            category_slug="restaurants",
            page=1,
        ),
        CrawlPlan(
            state="Lagos",
            city="Lekki",
            category_slug="banks",
            page=1,
        ),
    ]

    submitted = await service.submit(
        plans,
    )

    assert submitted == 2
    assert await queue.size() == 2

    first = await queue.dequeue()
    second = await queue.dequeue()

    assert first is not None
    assert second is not None

    assert first.source == Source.FINELIB
    assert first.state == "Lagos"
    assert first.city == "Yaba"
    assert first.category_slug == "restaurants"
    assert first.page == 1

    assert second.source == Source.FINELIB
    assert second.state == "Lagos"
    assert second.city == "Lekki"
    assert second.category_slug == "banks"
    assert second.page == 1

    assert await queue.is_empty()


@pytest.mark.asyncio
async def test_empty_plans_submit_nothing() -> None:

    queue = InMemoryJobQueue()

    scheduler = JobScheduler(
        queue=queue,
    )

    listing_builder = ListingUrlBuilder(
        taxonomy=CategoryProvider(),
        slug_mapper=FinelibUrlSlugMapper(),
    )

    service = CrawlPlanSubmissionService(
        listing_builder=listing_builder,
        job_factory=CrawlJobFactory(),
        scheduler=scheduler,
    )

    submitted = await service.submit(
        [],
    )

    assert submitted == 0
    assert await queue.is_empty()
