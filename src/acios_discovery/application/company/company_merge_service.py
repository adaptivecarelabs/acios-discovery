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

        company.add_source(
            discovery.source,
        )

        #
        # Refresh timestamp
        #

        company.touch()

        #
        # Enrichment
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

        if (
            company.year_founded is None
            and discovery.year_founded is not None
        ):
            company.year_founded = discovery.year_founded

        if (
            company.employee_count is None
            and discovery.employee_count is not None
        ):
            company.employee_count = discovery.employee_count

        if (
            company.business_locations is None
            and discovery.business_locations is not None
        ):
            company.business_locations = discovery.business_locations

        if (
            company.description is None
            and discovery.description is not None
        ):
            company.description = discovery.description

        return company

    
