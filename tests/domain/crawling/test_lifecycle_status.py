from acios_discovery.domain.crawling import (
    CrawlLifecycleStatus,
)


def test_status_values():

    assert CrawlLifecycleStatus.NEW == "NEW"

    assert CrawlLifecycleStatus.QUEUED == "QUEUED"

    assert CrawlLifecycleStatus.RUNNING == "RUNNING"

    assert CrawlLifecycleStatus.COMPLETED == "COMPLETED"

    assert CrawlLifecycleStatus.FAILED == "FAILED"

    assert CrawlLifecycleStatus.RETRYING == "RETRYING"

    assert CrawlLifecycleStatus.CANCELLED == "CANCELLED"
