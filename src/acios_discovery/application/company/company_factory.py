from __future__ import annotations

from datetime import UTC, datetime

from acios_discovery.application.company.company_id_allocator import (
    CompanyIdAllocator,
)
from acios_discovery.application.normalization.canonical_business_name import (
    CanonicalBusinessNameNormalizer,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.discovery.models import RawDiscovery


class CompanyFactory:
    """
    Creates a Company aggregate from a RawDiscovery.

    Company identity is supplied by the configured
    CompanyIdAllocator.

    Field values are established through the same
    merge_discovery() path used for subsequent merges,
    at full confidence, so a newly created company carries
    provenance for every field exactly like a merged one.
    """

    #
    # A founding discovery has no competing value to weigh
    # against, so it is recorded at maximum confidence.
    #

    FOUNDING_CONFIDENCE = 100.0

    def __init__(
        self,
        *,
        id_allocator: CompanyIdAllocator,
    ) -> None:
        self._normalizer = CanonicalBusinessNameNormalizer()
        self._id_allocator = id_allocator

    async def create(
        self,
        *,
        discovery: RawDiscovery,
    ) -> Company:

        canonical = self._normalizer.normalize(
            discovery.business_name,
        )

        company_id = await self._id_allocator.allocate()

        now = datetime.now(UTC)

        company = Company(
            id=company_id,
            canonical_name=canonical,
            first_seen=now,
            last_seen=now,
        )

        company.merge_discovery(
            discovery,
            confidence=self.FOUNDING_CONFIDENCE,
        )

        return company
