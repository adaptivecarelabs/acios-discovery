from __future__ import annotations

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
from acios_discovery.application.company.sequential_company_id_allocator import (
    SequentialCompanyIdAllocator,
)
from acios_discovery.application.discovery.detail_enrichment_engine import (
    DetailEnrichmentEngine,
)
from acios_discovery.application.discovery.discovery_batch_processor import (
    DiscoveryBatchProcessor,
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
from acios_discovery.application.planning.providers.category_provider import (
    CategoryProvider,
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
from acios_discovery.infrastructure.persistence.repositories.container import (
    PersistenceRepositories,
)
from acios_discovery.infrastructure.persistence.unit_of_work import (
    SqlAlchemyUnitOfWork,
)

from .crawling_services import CrawlingServices


class DiscoveryServices:
    """
    Composition root for the discovery subsystem.

    Infrastructure dependencies are supplied externally.

    The database repositories are bound to the AsyncSession
    supplied to this composition root.
    """

    def __init__(
        self,
        *,
        session: AsyncSession,
        workers: int = 4,
    ) -> None:
        self.http = HttpxClient()

        #
        # Persistence
        #

        self.repositories = PersistenceRepositories(
            session,
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
        # Detail enrichment
        #

        self.enricher = FinelibEnricher(
            http=self.http,
            parser=FinelibDetailParser(),
            mapper=FinelibDetailMapper(),
        )

        self.enrichment_engine = DetailEnrichmentEngine(
            enricher=self.enricher,
            repository=self.discovery_repository,
        )

        #
        # Discovery persistence
        #

        self.persistence = DiscoveryPersistenceService(
            unit_of_work=SqlAlchemyUnitOfWork(
                session=session,
            ),
        )

        #
        # Entity resolution
        #

        self.resolution_engine = (
            EntityResolutionEngine()
        )

        self.resolution_service = (
            EntityResolutionService(
                repository=self.company_repository,
                engine=self.resolution_engine,
            )
        )

        #
        # Company registry
        #

        self.company_id_allocator = (
            SequentialCompanyIdAllocator()
        )

        self.factory = CompanyFactory(
            id_allocator=self.company_id_allocator,
        )

        self.merge_service = CompanyMergeService()

        self.registry = (
            DiscoveryCompanyRegistryService(
                repository=self.company_repository,
                resolution_service=self.resolution_service,
                factory=self.factory,
                merge_service=self.merge_service,
            )
        )

        self.processor = DiscoveryProcessor(
            registry_service=self.registry,
        )

        self.batch_processor = (
            DiscoveryBatchProcessor(
                processor=self.processor,
            )
        )

        #
        # Authoritative discovery pipeline
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

        self.crawling = CrawlingServices(
            pipeline=self.discovery_pipeline,
            listing_builder=self.url_builder,
            workers=workers,
        )
