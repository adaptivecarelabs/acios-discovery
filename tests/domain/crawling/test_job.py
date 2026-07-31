from acios_discovery.domain.crawling.job import CrawlJob
from acios_discovery.domain.crawling.status import CrawlStatus


def test_job_defaults() -> None:
    job = CrawlJob(
        source="finelib",
        listing_url="https://www.finelib.com/cities/lagos/health",
        state="Lagos",
        city="Lagos",
        category_slug="health",
    )

    assert job.page == 1
    assert job.retries == 0
    assert job.status == CrawlStatus.PENDING
