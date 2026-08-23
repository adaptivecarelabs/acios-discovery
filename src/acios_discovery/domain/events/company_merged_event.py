from __future__ import annotations

from dataclasses import dataclass

from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.domain.company.merge_summary import MergeSummary
from acios_discovery.domain.events.crawl_event import CrawlEvent


@dataclass(slots=True, kw_only=True)
class CompanyMergedEvent(CrawlEvent):
    """
    Raised whenever new discovery data is merged
    into an existing Company.
    """

    company_id: CompanyId

    source: str

    detail_url: str | None

    summary: MergeSummary
