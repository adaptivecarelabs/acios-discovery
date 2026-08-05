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
            company.add_phone(
                phone,
            )

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

        #
        # Refresh timestamp
        #

        company.touch()

        return company
