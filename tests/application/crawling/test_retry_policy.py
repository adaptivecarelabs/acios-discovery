from acios_discovery.application.crawling.retry_policy import (
    RetryPolicy,
)
from acios_discovery.domain.crawling import (
    CrawlJob,
)
from acios_discovery.domain.sources import (
    Source,
)


def test_retry_allowed():

    job = CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.com",
        state="Lagos",
        city="Yaba",
        category_slug="restaurants",
        retries=0,
        max_retries=3,
    )

    assert RetryPolicy().should_retry(job)


def test_retry_denied():

    job = CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.com",
        state="Lagos",
        city="Yaba",
        category_slug="restaurants",
        retries=3,
        max_retries=3,
    )

    assert not RetryPolicy().should_retry(job)
