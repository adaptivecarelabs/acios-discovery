from acios_discovery.bootstrap.discovery_services import (
    DiscoveryServices,
)


def test_discovery_services_builds_complete_graph():
    services = DiscoveryServices(
        workers=4,
    )

    assert services.http is not None

    assert services.company_repository is not None
    assert services.discovery_repository is not None

    assert services.connector is not None
    assert services.downloader is not None

    assert services.category_provider is not None
    assert services.url_builder is not None

    assert services.crawl_engine is not None
    assert services.enrichment_engine is not None

    assert services.resolution_engine is not None
    assert services.resolution_service is not None

    assert services.factory is not None
    assert services.merge_service is not None
    assert services.registry is not None

    assert services.processor is not None
    assert services.batch_processor is not None

    assert services.crawling is not None
    assert services.crawling.queue is not None
    assert services.crawling.scheduler is not None
    assert services.crawling.job_factory is not None
    assert services.crawling.submission_service is not None
    assert services.crawling.worker_pool is not None
    assert services.crawling.supervisor is not None
