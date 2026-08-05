from __future__ import annotations

from acios_discovery.application.normalization.canonical_business_name import (
    CanonicalBusinessNameNormalizer,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.domain.discovery.models import RawDiscovery


class CompanyFactory:
    """
    Creates a Company aggregate from a RawDiscovery.
    """

    def __init__(
        self,
        normalizer: CanonicalBusinessNameNormalizer | None = None,
    ) -> None:
        self._normalizer = (
            normalizer
            or CanonicalBusinessNameNormalizer()
        )

    def create(
        self,
        sequence: int,
        discovery: RawDiscovery,
    ) -> Company:

        company = Company(
            id=CompanyId.from_sequence(sequence),
            canonical_name=self._normalizer.normalize(
                discovery.business_name,
            ),
        )

        #
        # Alias
        #

        company.add_alias(
            discovery.business_name,
        )

        #
        # Phones
        #

        for phone in discovery.phone_numbers:
            company.add_phone(phone)

        #
        # Email
        #

        if discovery.email:
            company.add_email(
                discovery.email,
            )

        #
        # Website
        #

        if discovery.website:
            company.add_website(
                discovery.website,
            )

        #
        # Address
        #

        if discovery.address:
            company.addresses.add(
                discovery.address,
            )

        #
        # Category
        #

        if discovery.category:
            company.categories.add(
                discovery.category,
            )

        #
        # City
        #

        if discovery.city:
            company.cities.add(
                discovery.city,
            )

        #
        # State
        #

        if discovery.state:
            company.states.add(
                discovery.state,
            )

        #
        # Source
        #

        company.sources.add(
            discovery.source,
        )

        return company
