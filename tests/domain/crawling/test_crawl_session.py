from acios_discovery.domain.crawling.crawl_session import CrawlSession
from acios_discovery.domain.crawling.crawl_session_status import (
    CrawlSessionStatus,
)


def test_session_lifecycle():

    session = CrawlSession()

    assert session.status is CrawlSessionStatus.PENDING

    session.start()

    assert session.status is CrawlSessionStatus.RUNNING
    assert session.started_at is not None

    session.complete()

    assert session.status is CrawlSessionStatus.COMPLETED
    assert session.finished_at is not None
