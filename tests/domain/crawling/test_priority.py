from acios_discovery.domain.crawling.priority import CrawlPriority


def test_priority_order() -> None:
    assert CrawlPriority.HIGH < CrawlPriority.NORMAL
    assert CrawlPriority.NORMAL < CrawlPriority.LOW
