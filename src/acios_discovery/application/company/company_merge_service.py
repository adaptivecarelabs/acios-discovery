from __future__ import annotations

from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.merge_summary import MergeSummary
from acios_discovery.domain.discovery.models import RawDiscovery


class CompanyMergeService:
    """
    Enriches an existing Company aggregate with newly
    discovered information, using confidence-weighted,
    provenance-tracked merging.
    """

    def merge(
        self,
        company: Company,
        discovery: RawDiscovery,
        *,
        confidence: float,
    ) -> MergeSummary:

        return company.merge_discovery(
            discovery,
            confidence=confidence,
        )
