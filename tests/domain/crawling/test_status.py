from acios_discovery.domain.crawling.status import CrawlStatus


def test_status_values() -> None:
    assert CrawlStatus.PENDING == "pending"
    assert CrawlStatus.RUNNING == "running"
    assert CrawlStatus.COMPLETED == "completed"
