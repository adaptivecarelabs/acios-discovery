from __future__ import annotations

from pydantic import BaseModel, Field

from acios_discovery.domain.discovery.record import DiscoveryRecord
from acios_discovery.domain.sources import Source


class ListingCrawlResult(BaseModel):
    """
    Result of crawling one complete listing.

    Contains page-level crawl statistics and the discovery
    records produced by the listing crawl.
    """

    pages_crawled: int = 0
    companies_discovered: int = 0
    records: list[DiscoveryRecord] = Field(
        default_factory=list,
    )

    @property
    def source(self) -> Source:
        """
        Return the source associated with the crawl records.
        """
        if not self.records:
            raise ValueError(
                "ListingCrawlResult has no records."
            )

        return self.records[0].context.source
