from __future__ import annotations

from acios_discovery.application.company.company_factory import CompanyFactory
from acios_discovery.application.company.company_merge_service import CompanyMergeService
from acios_discovery.application.company.discovery_company_registry_service import (
    DiscoveryCompanyRegistryService,
)
from acios_discovery.application.discovery.detail_enrichment_engine import (
    DetailEnrichmentEngine,
)
from acios_discovery.application.discovery.discovery_batch_processor import (
    DiscoveryBatchProcessor,
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
from acios_discovery.infrastructure.connectors.finelib.url_slug_mapper import FinelibUrlSlugMapper
from acios_discovery.infrastructure.http.httpx_client import HttpxClient
from acios_discovery.infrastructure.persistence.in_memory_discovery_repository import (
    InMemoryDiscoveryRepository,
)
from acios_discovery.infrastructure.repositories.in_memory_company_repository import (
    InMemoryCompanyRepository,
)


class DiscoveryServices:

    def __init__(self) -> None:

        self.http = HttpxClient()

        self.company_repository = InMemoryCompanyRepository()

        self.discovery_repository = (
            InMemoryDiscoveryRepository()
        )

        self.connector = FinelibConnector(
            parser=FinelibParser(),
            mapper=FinelibMapper(),
        )

        self.downloader = ListingDownloader(
            client=self.http,
        )

        self.category_provider = CategoryProvider()
        self.url_builder = ListingUrlBuilder(
            taxonomy = self.category_provider,
            slug_mapper=FinelibUrlSlugMapper()
        )

        self.crawl_engine = ListingCrawlEngine(
            downloader=self.downloader,
            connector=self.connector,
            repository=self.discovery_repository,
            url_builder=self.url_builder,
        )

        self.enricher = FinelibEnricher(
            http=self.http,
            parser=FinelibDetailParser(),
            mapper=FinelibDetailMapper(),
        )

        self.enrichment_engine = DetailEnrichmentEngine(
            enricher=self.enricher,
            repository=self.discovery_repository,
        )

        self.resolution_engine = EntityResolutionEngine()

        self.resolution_service = EntityResolutionService(
            repository=self.company_repository,
            engine=self.resolution_engine,
        )

        self.factory = CompanyFactory()

        self.merge_service = CompanyMergeService()

        self.registry = DiscoveryCompanyRegistryService(
            repository=self.company_repository,
            resolution_service=self.resolution_service,
            factory=self.factory,
            merge_service=self.merge_service,
        )

        self.processor = DiscoveryProcessor(
            registry_service=self.registry,
        )

        self.batch_processor = DiscoveryBatchProcessor(
            processor=self.processor,
        )
