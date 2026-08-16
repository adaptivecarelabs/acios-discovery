from unittest.mock import Mock

from acios_discovery.bootstrap.crawling_services import (
    CrawlingServices,
)


class FakeListingBuilder:
    pass


def test_crawling_services_builds_execution_graph():
    pipeline = Mock()

    services = CrawlingServices(
        pipeline=pipeline,
        listing_builder=FakeListingBuilder(),
        workers=4,
    )

    assert services.queue is not None
    assert services.scheduler is not None
    assert services.job_factory is not None
    assert services.submission_service is not None
    assert services.metrics is not None
    assert services.publisher is not None
    assert services.worker_factory is not None
    assert services.worker_pool is not None
    assert services.session is not None
    assert services.supervisor is not None
