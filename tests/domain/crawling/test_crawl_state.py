from acios_discovery.domain.crawling.crawl_state import CrawlState


def test_enum_values():

    assert CrawlState.CREATED.value == "CREATED"

    assert CrawlState.RUNNING.value == "RUNNING"

    assert CrawlState.COMPLETED.value == "COMPLETED"

    assert CrawlState.FAILED.value == "FAILED"
