from __future__ import annotations

from acios_discovery.application.crawling.crawl_job_factory import (
    CrawlJobFactory,
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


class CrawlPlanSubmissionService:
    """
    Converts crawl plans into executable crawl jobs
    and submits them to the crawl queue.

    This service does not execute crawl jobs.
    """

    def __init__(
        self,
        *,
        listing_builder: ListingUrlBuilder,
        job_factory: CrawlJobFactory,
        scheduler: JobScheduler,
    ) -> None:

        self._listing_builder = listing_builder
        self._job_factory = job_factory
        self._scheduler = scheduler

    async def submit(
        self,
        plans: list[CrawlPlan],
    ) -> int:

        if not plans:
            return 0

        jobs = []

        for plan in plans:

            listing = self._listing_builder.build(
                plan,
            )

            job = self._job_factory.create(
                plan=plan,
                listing=listing,
            )

            jobs.append(job)

        await self._scheduler.schedule(
            jobs,
        )

        return len(jobs)
