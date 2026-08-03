from datetime import datetime, timedelta

from acios_discovery.application.crawling.crawl_summary import (
    CrawlSummary,
)


def test_duration():

    start = datetime.now()

    end = start + timedelta(seconds=12)

    summary = CrawlSummary(
        started_at=start,
        finished_at=end,
    )

    assert summary.duration_seconds == 12
