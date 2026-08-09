from __future__ import annotations

from acios_discovery.domain.discovery.context import (
    DiscoveryContext,
)
from acios_discovery.domain.discovery.models import (
    RawDiscovery,
)
from acios_discovery.domain.discovery.record import (
    DiscoveryRecord,
)
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.persistence.orm.discovery import (
    DiscoveryORM,
)


class DiscoveryMapper:
    """
    Converts between DiscoveryRecord and DiscoveryORM.
    """

    @staticmethod
    def to_orm(
        record: DiscoveryRecord,
    ) -> DiscoveryORM:
        """
        Convert a DiscoveryRecord into DiscoveryORM.
        """

        return DiscoveryORM(
            #
            # Company
            #
            source=str(record.company.source),
            business_name=record.company.business_name,
            address=record.company.address,
            description=record.company.description,
            detail_url=record.company.detail_url,

            #
            # Detail enrichment
            #
            phone_numbers=record.company.phone_numbers,
            email=record.company.email,
            website=record.company.website,
            social_links=record.company.social_links,
            product_types=record.company.product_types,
            payment_methods=record.company.payment_methods,
            year_founded=record.company.year_founded,
            employee_count=record.company.employee_count,
            business_locations=record.company.business_locations,

            #
            # Discovery Context
            #
            country=record.context.country,
            state=record.context.state,
            city=record.context.city,
            root=record.context.root,
            industry=record.context.industry,
            sector=record.context.sector,
            category=record.context.category,
            subcategory=record.context.subcategory,
            listing_url=record.context.listing_url,
            page_number=record.context.page_number,

            #
            # Timestamp
            #
            discovered_at=record.context.discovered_at,
        )


    @staticmethod
    def to_domain(
        orm: DiscoveryORM,
    ) -> DiscoveryRecord:
        """
        Convert DiscoveryORM back into DiscoveryRecord.
        """

        company = RawDiscovery(
            source=Source(orm.source),
            business_name=orm.business_name,
            detail_url=orm.detail_url,
            address=orm.address,
            description=orm.description,

            #
            # Detail enrichment
            #
            phone_numbers=orm.phone_numbers,
            email=orm.email,
            website=orm.website,
            social_links=orm.social_links,
            product_types=orm.product_types,
            payment_methods=orm.payment_methods,
            year_founded=orm.year_founded,
            employee_count=orm.employee_count,
            business_locations=orm.business_locations,

            #
            # Metadata
            #
            category=orm.category,
            city=orm.city,
            state=orm.state,
            discovered_at=orm.discovered_at,
        )

        context = DiscoveryContext(
            source=Source(orm.source),
            country=orm.country,
            state=orm.state,
            city=orm.city,
            root=orm.root,
            industry=orm.industry,
            sector=orm.sector,
            category=orm.category,
            subcategory=orm.subcategory,
            listing_url=orm.listing_url,
            page_number=orm.page_number,
            discovered_at=orm.discovered_at,
        )

        return DiscoveryRecord(
            company=company,
            context=context,
        )


    @staticmethod
    def update_orm(
        orm: DiscoveryORM,
        record: DiscoveryRecord,
    ) -> None:
        """
        Update an existing DiscoveryORM from a DiscoveryRecord.
        """

        #
        # Company
        #

        orm.source = str(
            record.company.source
        )

        orm.business_name = (
            record.company.business_name
        )

        orm.address = (
            record.company.address
        )

        orm.description = (
            record.company.description
        )

        orm.detail_url = (
            record.company.detail_url
        )

        #
        # Detail enrichment
        #

        orm.phone_numbers = (
            record.company.phone_numbers
        )

        orm.email = (
            record.company.email
        )

        orm.website = (
            record.company.website
        )

        orm.social_links = (
            record.company.social_links
        )

        orm.product_types = (
            record.company.product_types
        )

        orm.payment_methods = (
            record.company.payment_methods
        )

        orm.year_founded = (
            record.company.year_founded
        )

        orm.employee_count = (
            record.company.employee_count
        )

        orm.business_locations = (
            record.company.business_locations
        )

        #
        # Discovery Context
        #

        orm.country = (
            record.context.country
        )

        orm.state = (
            record.context.state
        )

        orm.city = (
            record.context.city
        )

        orm.root = (
            record.context.root
        )

        orm.industry = (
            record.context.industry
        )

        orm.sector = (
            record.context.sector
        )

        orm.category = (
            record.context.category
        )

        orm.subcategory = (
            record.context.subcategory
        )

        orm.listing_url = (
            record.context.listing_url
        )

        orm.page_number = (
            record.context.page_number
        )

        orm.discovered_at = (
            record.context.discovered_at
        )
