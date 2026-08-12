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
    """

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

        company = Company(
            id=company_id,
            canonical_name=canonical,
            description=discovery.description,
            first_seen=datetime.now(UTC),
            last_seen=datetime.now(UTC),
        )

        #
        # Listing data
        #

        company.add_alias(
            discovery.business_name,
        )

        for phone in discovery.phone_numbers:
            company.add_phone(phone)

        company.add_address(
            discovery.address,
        )

        if discovery.category:
            company.categories.add(
                discovery.category,
            )

        if discovery.city:
            company.cities.add(
                discovery.city,
            )

        if discovery.state:
            company.states.add(
                discovery.state,
            )

        company.add_source(
            discovery.source,
        )

        #
        # Detail enrichment
        #

        company.add_email(
            discovery.email,
        )

        company.add_website(
            discovery.website,
        )

        company.social_links.update(
            discovery.social_links,
        )

        company.product_types.update(
            discovery.product_types,
        )

        company.payment_methods.update(
            discovery.payment_methods,
        )

        company.year_founded = (
            discovery.year_founded
        )

        company.employee_count = (
            discovery.employee_count
        )

        company.business_locations = (
            discovery.business_locations
        )

        return company
