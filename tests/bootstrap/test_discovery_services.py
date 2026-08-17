from unittest.mock import MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.bootstrap.discovery_services import (
    DiscoveryServices,
)


def test_discovery_services_builds_complete_graph() -> None:
    session = MagicMock(
        spec=AsyncSession,
    )

    services = DiscoveryServices(
        session=session,
        workers=4,
    )

    assert services.http is not None

    #
    # Persistence
    #

    assert services.repositories is not None
    assert services.company_repository is not None
    assert services.discovery_repository is not None

    #
    # Finelib
    #

    assert services.connector is not None
    assert services.downloader is not None

    #
    # Planning
    #

    assert services.category_provider is not None
    assert services.city_provider is not None
    assert services.plan_generator is not None
    assert services.url_builder is not None

    #
    # Crawl
    #

    assert services.crawl_engine is not None

    #
    # Enrichment
    #

    assert services.enricher is not None
    assert services.enrichment_engine is not None

    #
    # Resolution
    #

    assert services.resolution_engine is not None
    assert services.resolution_service is not None

    #
    # Company registry
    #

    assert services.company_id_allocator is not None
    assert services.factory is not None
    assert services.merge_service is not None
    assert services.registry is not None

    #
    # Processing
    #

    assert services.processor is not None
    assert services.batch_processor is not None

    #
    # Crawling execution subsystem
    #

    assert services.crawling is not None
    assert services.crawling.queue is not None
    assert services.crawling.scheduler is not None
    assert services.crawling.job_factory is not None
    assert services.crawling.submission_service is not None
    assert services.crawling.worker_pool is not None
    assert services.crawling.supervisor is not None

    #
    # Discovery execution
    #

    assert services.execution_service is not None
