from __future__ import annotations

from acios_discovery.application.crawling.concurrent_worker_pool import (
    ConcurrentWorkerPool,
)
from acios_discovery.application.crawling.crawl_job_factory import (
    CrawlJobFactory,
)
from acios_discovery.application.crawling.crawl_plan_submission_service import (
    CrawlPlanSubmissionService,
)
from acios_discovery.application.crawling.crawl_worker import (
    CrawlWorker,
)
from acios_discovery.application.crawling.crawl_worker_factory import (
    CrawlWorkerFactory,
)
from acios_discovery.application.crawling.job_scheduler import (
    JobScheduler,
)
from acios_discovery.application.crawling.supervision.crawl_supervisor import (
    CrawlSupervisor,
)
from acios_discovery.application.events.in_memory_event_publisher import (
    InMemoryEventPublisher,
)
from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
)
from acios_discovery.application.planning.builders.listing_url_builder import (
    ListingUrlBuilder,
)
from acios_discovery.domain.crawling.crawl_session import (
    CrawlSession,
)
from acios_discovery.infrastructure.queue.in_memory_job_queue import (
    InMemoryJobQueue,
)


class CrawlingServices:
    """
    Composition root for the crawl execution subsystem.

    This class contains dependency wiring only.
    It does not contain crawling business logic.
    """

    def __init__(
        self,
        *,
        crawl_engine,
        listing_builder: ListingUrlBuilder,
        workers: int = 4,
    ) -> None:
        self.queue = InMemoryJobQueue()

        self.scheduler = JobScheduler(
            self.queue,
        )

        self.job_factory = CrawlJobFactory()

        self.submission_service = CrawlPlanSubmissionService(
            listing_builder=listing_builder,
            job_factory=self.job_factory,
            scheduler=self.scheduler,
        )

        self.metrics = CrawlMetricsService()

        self.publisher = InMemoryEventPublisher()

        def create_worker() -> CrawlWorker:
            return CrawlWorker(
                engine=crawl_engine,
            )

        self.worker_factory: CrawlWorkerFactory = create_worker

        self.worker_pool = ConcurrentWorkerPool(
            queue=self.queue,
            worker_factory=self.worker_factory,
            metrics=self.metrics,
            publisher=self.publisher,
            workers=workers,
        )

        self.session = CrawlSession()

        self.supervisor = CrawlSupervisor(
            session=self.session,
            worker_pool=self.worker_pool,
            metrics=self.metrics,
        )
