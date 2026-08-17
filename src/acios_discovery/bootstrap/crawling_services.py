from __future__ import annotations

from collections.abc import Callable
from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession

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
    PipelineFactory,
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
from acios_discovery.application.discovery.pipeline import (
    DiscoveryPipeline,
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
from acios_discovery.application.subscribers.crawl_metrics_subscriber import (
    CrawlMetricsSubscriber,
)
from acios_discovery.domain.crawling.crawl_session import (
    CrawlSession,
)
from acios_discovery.infrastructure.persistence.database import (
    SessionFactory,
)
from acios_discovery.infrastructure.queue.in_memory_job_queue import (
    InMemoryJobQueue,
)


class CrawlingServices:
    """
    Composition root for the crawl execution subsystem.

    The preferred execution model is:

        job
          |
          v
        CrawlWorker
          |
          +--> worker-specific AsyncSession
          |
          +--> worker-specific DiscoveryPipeline
          |
          v
        database

    Non-database infrastructure remains shared.

    The optional ``pipeline`` argument is retained for compatibility
    with isolated bootstrap tests and older callers. Production
    execution should use ``pipeline_factory`` together with
    ``session_factory``.
    """

    def __init__(
        self,
        *,
        listing_builder: ListingUrlBuilder,
        workers: int = 4,
        pipeline_factory: PipelineFactory | None = None,
        session_factory: Callable[
            [],
            AsyncSession,
        ] = SessionFactory,
        pipeline: DiscoveryPipeline | None = None,
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

        self.metrics_subscriber = CrawlMetricsSubscriber(
            metrics=self.metrics,
        )

        self.publisher.subscribe(
            self.metrics_subscriber,
        )

        #
        # Worker construction
        #
        # Preferred path:
        #
        #     pipeline_factory + session_factory
        #
        # Compatibility path:
        #
        #     pipeline=
        #
        # The compatibility pipeline is only used when explicitly
        # supplied. The normal DiscoveryServices composition root
        # always supplies a worker-specific pipeline factory.
        #

        if pipeline_factory is None:
            if pipeline is None:
                raise TypeError(
                    "CrawlingServices requires either "
                    "pipeline_factory or pipeline."
                )

            fixed_pipeline = cast(
                DiscoveryPipeline,
                pipeline,
            )

            def create_worker() -> CrawlWorker:
                return CrawlWorker(
                    session_factory=session_factory,
                    pipeline_factory=(
                        lambda _session: fixed_pipeline
                    ),
                )

        else:

            def create_worker() -> CrawlWorker:
                return CrawlWorker(
                    session_factory=session_factory,
                    pipeline_factory=pipeline_factory,
                )

        self.worker_factory: CrawlWorkerFactory = create_worker

        self.worker_pool = ConcurrentWorkerPool(
            queue=self.queue,
            worker_factory=self.worker_factory,
            publisher=self.publisher,
            workers=workers,
        )

        self.session = CrawlSession()

        self.supervisor = CrawlSupervisor(
            session=self.session,
            worker_pool=self.worker_pool,
        )
