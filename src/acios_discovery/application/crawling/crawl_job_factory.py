from __future__ import annotations

from acios_discovery.application.planning.models import (
    CrawlPlan,
    ListingUrl,
)
from acios_discovery.domain.crawling import CrawlJob


class CrawlJobFactory:
    """
    Creates executable crawl jobs from crawl plans and
    generated listing URLs.
    """

    def create(
        self,
        *,
        plan: CrawlPlan,
        listing: ListingUrl,
    ) -> CrawlJob:

        return CrawlJob(
            source=listing.source,
            listing_url=listing.url,
            state=plan.state,
            city=plan.city,
            category_slug=plan.category_slug,
            page=plan.page,
        )
