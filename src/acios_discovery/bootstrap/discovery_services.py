from __future__ import annotations

from collections.abc import Callable
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.application.company.company_factory import (
    CompanyFactory,
)
from acios_discovery.application.company.company_merge_service import (
    CompanyMergeService,
)
from acios_discovery.application.company.discovery_company_registry_service import (
    DiscoveryCompanyRegistryService,
)
from acios_discovery.application.discovery.detail_enrichment_engine import (
    DetailEnrichmentEngine,
)
from acios_discovery.application.discovery.discovery_batch_processor import (
    DiscoveryBatchProcessor,
)
from acios_discovery.application.discovery.discovery_execution_service import (
    DiscoveryExecutionService,
)
from acios_discovery.application.discovery.discovery_persistence_service import (
    DiscoveryPersistenceService,
)
from acios_discovery.application.discovery.discovery_processor import (
    DiscoveryProcessor,
)
from acios_discovery.application.discovery.listing_crawl_engine import (
    ListingCrawlEngine,
)
from acios_discovery.application.discovery.listing_downloader import (
    ListingDownloader,
)
from acios_discovery.application.discovery.pipeline import (
    DiscoveryPipeline,
)
from acios_discovery.application.enrichment.finelib_enricher import (
    FinelibEnricher,
)
from acios_discovery.application.planning.builders.listing_url_builder import (
    ListingUrlBuilder,
)
from acios_discovery.application.planning.crawl_plan_generator import (
    CrawlPlanGenerator,
)
from acios_discovery.application.planning.providers.category_provider import (
    CategoryProvider,
)
from acios_discovery.application.planning.providers.city_provider import (
    CityProvider,
)
from acios_discovery.application.resolution.entity_resolution_engine import (
    EntityResolutionEngine,
)
from acios_discovery.application.resolution.entity_resolution_service import (
    EntityResolutionService,
)
from acios_discovery.infrastructure.connectors.finelib.connector import (
    FinelibConnector,
)
from acios_discovery.infrastructure.connectors.finelib.detail_mapper import (
    FinelibDetailMapper,
)
from acios_discovery.infrastructure.connectors.finelib.detail_parser import (
    FinelibDetailParser,
)
from acios_discovery.infrastructure.connectors.finelib.listing_mapper import (
    FinelibMapper,
)
from acios_discovery.infrastructure.connectors.finelib.listing_parser import (
    FinelibParser,
)
from acios_discovery.infrastructure.connectors.finelib.url_slug_mapper import (
    FinelibUrlSlugMapper,
)
from acios_discovery.infrastructure.http.httpx_client import (
    HttpxClient,
)
from acios_discovery.infrastructure.persistence.database import (
    SessionFactory,
)
from acios_discovery.infrastructure.persistence.repositories.container import (
    PersistenceRepositories,
)
from acios_discovery.infrastructure.persistence.unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from acios_discovery.infrastructure.persistence.repositories.sequence_company_id_allocator import (
    SequenceCompanyIdAllocator,
)
from .crawling_services import CrawlingServices
from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
)
from acios_discovery.infrastructure.http.metrics_recording_http_client import (
    MetricsRecordingHttpClient,
)



class DiscoveryServices:
    """
    Composition root for the discovery subsystem.

    Shared infrastructure such as HTTP clients, connectors,
    crawl engines and stateless enrichment infrastructure is
    constructed once.

    Database-bound discovery components used by concurrent
    crawl workers are constructed inside _build_pipeline()
    using the worker-specific AsyncSession.

    The public attributes retained here represent the complete
    discovery composition graph and are useful for bootstrap
    inspection and compatibility with existing callers.
    """

    def __init__(
        self,
        *,
        session: AsyncSession,
        workers: int = 4,
        http: Any | None = None,
        planner: CrawlPlanGenerator | None = None,
        session_factory: Callable[[], AsyncSession] | None = None,
        resume_session_id: str | None = None,
        metrics: CrawlMetricsService | None = None,
    ) -> None:
        

        #
        # Metrics service is constructed here, before anything
        # captures a reference to self.http — ListingDownloader
        # and FinelibEnricher below capture self.http at
        # construction time, so http must already be the
        # metrics-wrapped instance by the time they're built.
        #

        self.metrics = metrics or CrawlMetricsService()

        self.http = MetricsRecordingHttpClient(
            client=http or HttpxClient(),
            metrics=self.metrics,
        )


        #
        # Worker database session factory
        #
        # Production uses the application's SessionFactory.
        # Integration tests may inject a factory bound to their
        # isolated test database.
        #

        self.session_factory = (
            session_factory
            or SessionFactory
        )


        #
        # Persistence
        #

        self.repositories = PersistenceRepositories(
            session,
        )

        self.unit_of_work = SqlAlchemyUnitOfWork(
            session=session,
        )

        self.company_repository = (
            self.repositories.company
        )

        self.discovery_repository = (
            self.repositories.discovery
        )

        #
        # Finelib listing connector
        #

        self.connector = FinelibConnector(
            parser=FinelibParser(),
            mapper=FinelibMapper(),
        )

        self.downloader = ListingDownloader(
            client=self.http,
        )

        #
        # Planning
        #

        self.category_provider = CategoryProvider()

        self.city_provider = CityProvider()

        self.plan_generator = planner or CrawlPlanGenerator(
            city_provider=self.city_provider,
            category_provider=self.category_provider,
        )

        self.url_builder = ListingUrlBuilder(
            taxonomy=self.category_provider,
            slug_mapper=FinelibUrlSlugMapper(),
        )

        #
        # Listing crawl
        #

        self.crawl_engine = ListingCrawlEngine(
            downloader=self.downloader,
            connector=self.connector,
            url_builder=self.url_builder,
        )

        #
        # Detail enrichment infrastructure
        #

        self.enricher = FinelibEnricher(
            http=self.http,
            parser=FinelibDetailParser(),
            mapper=FinelibDetailMapper(),
        )

        #
        # Compatibility enrichment graph
        #
        # This public instance is bound to the composition-root
        # session. It exists for graph inspection and compatibility.
        #
        # Concurrent workers do NOT use this instance.
        # _build_pipeline() creates worker-specific instances.
        #

        self.enrichment_engine = DetailEnrichmentEngine(
            enricher=self.enricher,
            repository=self.discovery_repository,
        )

        #
        # Compatibility resolution graph
        #
        # These public components preserve the complete
        # DiscoveryServices composition graph.
        #
        # Worker execution creates equivalent database-bound
        # components inside _build_pipeline().
        #

        self.resolution_engine = (
            EntityResolutionEngine()
        )


        self.company_match_repository = (
            self.repositories.company_match
        )

        self.resolution_service = (
            EntityResolutionService(
                repository=self.company_match_repository,
                engine=self.resolution_engine,
            )
        )

        #
        # Company registry
        #

        self.company_id_allocator = (
            SequenceCompanyIdAllocator(
                session,
            )
        )

        self.factory = CompanyFactory(
            id_allocator=self.company_id_allocator,
        )

        self.merge_service = CompanyMergeService()

        self.registry = (
            DiscoveryCompanyRegistryService(
                unit_of_work=self.unit_of_work,
                resolution_service=self.resolution_service,
                factory=self.factory,
                merge_service=self.merge_service,
                metrics=self.metrics,
            )
        )

        #
        # Discovery processor
        #

        self.processor = DiscoveryProcessor(
            registry_service=self.registry,
        )

        self.batch_processor = (
            DiscoveryBatchProcessor(
                processor=self.processor,
            )
        )

                #
        # Compatibility persistence graph
        #

        self.persistence = DiscoveryPersistenceService(
            unit_of_work=self.unit_of_work,
        )

        #
        # Compatibility discovery pipeline
        #
        # Retained as a public composition-graph component.
        # CrawlWorker execution does not share this database-bound
        # pipeline between concurrent workers.
        #

        self.discovery_pipeline = DiscoveryPipeline(
            crawler=self.crawl_engine,
            enricher=self.enrichment_engine,
            persistence=self.persistence,
            processor=self.batch_processor,
        )

        #
        # Crawling execution subsystem
        #
        # IMPORTANT:
        # Workers use _build_pipeline(), not discovery_pipeline.
        #

        self.crawling = CrawlingServices(
            pipeline_factory=self._build_pipeline,
            session_factory=self.session_factory,
            listing_builder=self.url_builder,
            workers=workers,
            resume_session_id=resume_session_id,
            metrics=self.metrics,
        )

        #
        # Discovery execution
        #

        self.execution_service = DiscoveryExecutionService(
            planner=self.plan_generator,
            job_submission_service=(
                self.crawling.submission_service
            ),
            crawl_supervisor=self.crawling.supervisor,
            crawl_job_repository=self.repositories.crawl_job,
            resume_session_id=resume_session_id,
        )

    def _build_pipeline(
        self,
        session: AsyncSession,
    ) -> DiscoveryPipeline:
        """
        Build a complete database-bound discovery pipeline
        for one crawl worker.

        Every worker receives its own AsyncSession and therefore
        its own repositories, enrichment engine, resolution
        services, company registry and persistence unit of work.
        """

        repositories = PersistenceRepositories(
            session,
        )

        discovery_repository = repositories.discovery
        company_repository = repositories.company
        company_match_repository = repositories.company_match

        #
        # Enrichment
        #

        enrichment_engine = DetailEnrichmentEngine(
            enricher=self.enricher,
            repository=discovery_repository,
        )

        #
        # Persistence
        #

        unit_of_work = SqlAlchemyUnitOfWork(
            session = session,
        )

        persistence = DiscoveryPersistenceService(
            unit_of_work=unit_of_work,
        )

        #
        # Entity resolution
        #

        resolution_engine = EntityResolutionEngine()

        resolution_service = EntityResolutionService(
            repository=company_match_repository,
            engine=resolution_engine,
        )

        #
        # Company registry
        #

        company_id_allocator = (
            SequenceCompanyIdAllocator(
                session,
            )
        )

        factory = CompanyFactory(
            id_allocator=company_id_allocator,
        )

        merge_service = CompanyMergeService()

        registry = DiscoveryCompanyRegistryService(
            unit_of_work=unit_of_work,
            resolution_service=resolution_service,
            factory=factory,
            merge_service=merge_service,
            metrics=self.metrics,
        )

        #
        # Discovery processing
        #

        processor = DiscoveryProcessor(
            registry_service=registry,
        )

        batch_processor = DiscoveryBatchProcessor(
            processor=processor,
        )

        #
        # Worker-specific authoritative pipeline
        #

        return DiscoveryPipeline(
            crawler=self.crawl_engine,
            enricher=enrichment_engine,
            persistence=persistence,
            processor=batch_processor,
        )
