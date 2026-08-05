from __future__ import annotations

from dataclasses import dataclass

from acios_discovery.domain.discovery.record import DiscoveryRecord
from acios_discovery.domain.events.crawl_event import (
    CrawlEvent,
)


@dataclass(slots=True, kw_only=True)
class CompanyDiscoveredEvent(
    CrawlEvent,
):
    """
    Raised whenever a company
    has been discovered.
    """

    record: DiscoveryRecord
