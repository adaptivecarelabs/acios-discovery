from __future__ import annotations

from acios_discovery.domain.company.company import Company
from acios_discovery.domain.discovery.models import RawDiscovery


class CompanyMergeService:
    """
    Enriches an existing Company aggregate
    with newly discovered information.
    """

    def merge(
        self,
        company: Company,
        discovery: RawDiscovery,
    ) -> Company:

        company.merge_discovery(
            discovery,
        )

        return company
