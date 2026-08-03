from acios_discovery.application.crawling.crawl_job_factory import (
    CrawlJobFactory,
)
from acios_discovery.application.planning.models import (
    CrawlPlan,
    ListingUrl,
)
from acios_discovery.domain.crawling import (
    CrawlPriority,
    CrawlStatus,
)
from acios_discovery.domain.sources import Source


def test_creates_crawl_job():

    plan = CrawlPlan(
        state="Lagos",
        city="Yaba",
        category_slug="restaurants",
        page=1,
    )

    listing = ListingUrl(
        source=Source.FINELIB,
        url="https://example.com",
        state="Lagos",
        city="Yaba",
        taxonomy_slug="restaurants",
        page=1,
    )

    factory = CrawlJobFactory()

    job = factory.create(
        plan=plan,
        listing=listing,
    )

    assert job.state == "Lagos"

    assert job.city == "Yaba"

    assert job.category_slug == "restaurants"

    assert job.page == 1

    assert job.source == Source.FINELIB

    assert job.listing_url == "https://example.com"

    assert job.priority == CrawlPriority.NORMAL

    assert job.status == CrawlStatus.PENDING
