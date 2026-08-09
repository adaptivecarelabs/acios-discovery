import pytest

from acios_discovery.application.crawling.crawl_job_factory import (
    CrawlJobFactory,
)
from acios_discovery.application.crawling.crawl_pipeline import (
    CrawlPipeline,
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
from acios_discovery.infrastructure.connectors.finelib.url_slug_mapper import (
    FinelibUrlSlugMapper,
)
from acios_discovery.infrastructure.queue.in_memory_job_queue import (
    InMemoryJobQueue,
)


@pytest.mark.asyncio
async def test_pipeline_schedules_jobs():

    queue = InMemoryJobQueue()

    scheduler = JobScheduler(
        queue=queue,
    )

    builder = ListingUrlBuilder(
        taxonomy=CategoryProvider(),
        slug_mapper=FinelibUrlSlugMapper(),
    )

    factory = CrawlJobFactory()

    pipeline = CrawlPipeline(
        listing_builder=builder,
        job_factory=factory,
        scheduler=scheduler,
    )

    plans = [
        CrawlPlan(
            state="Lagos",
            city="Yaba",
            category_slug="restaurants",
        ),
        CrawlPlan(
            state="Lagos",
            city="Lekki",
            category_slug="banks",
        ),
    ]

    await pipeline.submit(
        plans,
    )

    assert await queue.size() == 2
