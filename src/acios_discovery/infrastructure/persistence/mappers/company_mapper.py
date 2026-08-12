from __future__ import annotations

from acios_discovery.application.normalization.company_lookup import (
    normalize_company_alias,
    normalize_company_email,
    normalize_company_name,
    normalize_company_phone,
    normalize_company_website,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.infrastructure.persistence.orm import (
    AddressORM,
    CategoryORM,
    CityORM,
    CompanyAliasORM,
    CompanyORM,
    EmailORM,
    PaymentMethodORM,
    PhoneNumberORM,
    ProductTypeORM,
    SocialLinkORM,
    SourceORM,
    StateORM,
    WebsiteORM,
)


class CompanyMapper:
    """
    Converts between the Company domain aggregate
    and SQLAlchemy ORM models.
    """

    @staticmethod
    def to_orm(
        company: Company,
    ) -> CompanyORM:

        orm = CompanyORM(
            id=company.id.value,
            canonical_name=company.canonical_name,
            description=company.description,
            confidence=company.confidence,
            active=company.active,
            year_founded=company.year_founded,
            employee_count=company.employee_count,
            business_locations=company.business_locations,
            first_seen=company.first_seen,
            last_seen=company.last_seen,
            canonical_name_normalized=normalize_company_name(
                company.canonical_name
            )
        )

        #
        # Identity
        #

        orm.aliases = [
            CompanyAliasORM(
                value=value,
                normalized_value=normalize_company_alias(
                    value,
                )
            )
            for value in sorted(company.aliases)
        ]

        orm.emails = [
            EmailORM(
                value=value,
                normalized_value=normalize_company_email(
                    value,
                )
            )
            for value in sorted(company.emails)
        ]

        orm.websites = [
            WebsiteORM(
                value=value,
                normalized_value=normalize_company_website(
                    value,
                )
            )
            for value in sorted(company.websites)
        ]

        orm.addresses = [
            AddressORM(value=value)
            for value in sorted(company.addresses)
        ]

        orm.phone_numbers = [
            PhoneNumberORM(
                value=value,
                normalized_value=normalize_company_phone(
                    value,
                )
            )
            for value in sorted(company.phone_numbers)
        ]

        #
        # Classification
        #

        orm.categories = [
            CategoryORM(value=value)
            for value in sorted(company.categories)
        ]

        orm.cities = [
            CityORM(value=value)
            for value in sorted(company.cities)
        ]

        orm.states = [
            StateORM(value=value)
            for value in sorted(company.states)
        ]

        orm.sources = [
            SourceORM(value=value)
            for value in sorted(company.sources)
        ]

        #
        # Enrichment
        #

        orm.product_types = [
            ProductTypeORM(value=value)
            for value in sorted(company.product_types)
        ]

        orm.payment_methods = [
            PaymentMethodORM(value=value)
            for value in sorted(company.payment_methods)
        ]

        #
        # Social links
        #
        # Temporary implementation.
        # We'll improve SocialLinkORM shortly.
        #

        orm.social_links = [
            SocialLinkORM(
                value=f"{platform}|{url}",
            )
            for platform, url
            in sorted(company.social_links.items())
        ]

        return orm




    @staticmethod
    def to_domain(
        orm: CompanyORM,
    ) -> Company:
        """
        Convert a SQLAlchemy CompanyORM
        into the Company domain aggregate.
        """

        company = Company(
            id=CompanyId.parse(orm.id),
            canonical_name=orm.canonical_name,
            description=orm.description,
            confidence=orm.confidence,
            active=orm.active,
            year_founded=orm.year_founded,
            employee_count=orm.employee_count,
            business_locations=orm.business_locations,
            first_seen=orm.first_seen,
            last_seen=orm.last_seen,
        )

        #
        # Identity
        #

        company.aliases.update(
            row.value
            for row in orm.aliases
        )


        company.emails.update(
            row.value
            for row in orm.emails
        )

        company.websites.update(
            row.value
            for row in orm.websites
        )

        company.addresses.update(
            row.value
            for row in orm.addresses
        )

        company.phone_numbers.update(
            row.value
            for row in orm.phone_numbers
        )

        #
        # Classification
        #

        company.categories.update(
            row.value
            for row in orm.categories
        )

        company.cities.update(
            row.value
            for row in orm.cities
        )

        company.states.update(
            row.value
            for row in orm.states
        )

        company.sources.update(
            row.value
            for row in orm.sources
        )

        #
        # Enrichment
        #

        company.product_types.update(
            row.value
            for row in orm.product_types
        )

        company.payment_methods.update(
            row.value
            for row in orm.payment_methods
        )

        #
        # Temporary social link parsing.
        #

        for row in orm.social_links:

            if "|" not in row.value:
                continue

            platform, url = row.value.split(
                "|",
                1,
            )

            company.social_links[platform] = url

        return company


    @staticmethod
    def _sync_collection(
        orm_collection,
        new_values,
        orm_factory,
        value_normalizer=None,
    ) -> None:
        """
        Synchronize a one-to-many child collection.

        Existing rows that are no longer present
        are removed.

        Missing rows are inserted.

        Existing rows are preserved.
        """

        existing = {
            item.value: item
            for item in orm_collection
        }

        wanted = set(new_values)

        #
        # Remove deleted values
        #

        orm_collection[:] = [
            item
            for item in orm_collection
            if item.value in wanted
        ]

        #
        # Add missing values
        #

        for value in sorted(
            wanted - existing.keys(),
        ):
            kwargs = {
                "value": value,
            }

            if value_normalizer is not None:
                kwargs["normalized_value"] = value_normalizer(
                    value,
                )

            orm_collection.append(
                orm_factory(
                    **kwargs,
                )
            )

            

    @classmethod
    def update_orm(
        cls,
        orm: CompanyORM,
        company: Company,
    ) -> None:
        """
        Update an existing ORM object from the
        current Company aggregate.
        """

        orm.canonical_name = company.canonical_name
        orm.canonical_name_normalized=normalize_company_name(
            company.canonical_name,
        )
        orm.description = company.description
        orm.confidence = company.confidence
        orm.active = company.active
        orm.year_founded = company.year_founded
        orm.employee_count = company.employee_count
        orm.business_locations = company.business_locations
        orm.last_seen = company.last_seen

        #
        # Identity
        #

        cls._sync_collection(
            orm.aliases,
            company.aliases,
            CompanyAliasORM,
            normalize_company_alias,
        )

        cls._sync_collection(
            orm.emails,
            company.emails,
            EmailORM,
            normalize_company_email,
        )

        cls._sync_collection(
            orm.websites,
            company.websites,
            WebsiteORM,
            normalize_company_website,
        )

        cls._sync_collection(
            orm.addresses,
            company.addresses,
            AddressORM,
        )

        cls._sync_collection(
            orm.phone_numbers,
            company.phone_numbers,
            PhoneNumberORM,
            normalize_company_phone,
        )

        #
        # Classification
        #

        cls._sync_collection(
            orm.categories,
            company.categories,
            CategoryORM,
        )

        cls._sync_collection(
            orm.cities,
            company.cities,
            CityORM,
        )

        cls._sync_collection(
            orm.states,
            company.states,
            StateORM,
        )

        cls._sync_collection(
            orm.sources,
            company.sources,
            SourceORM,
        )

        #
        # Enrichment
        #

        cls._sync_collection(
            orm.product_types,
            company.product_types,
            ProductTypeORM,
        )

        cls._sync_collection(
            orm.payment_methods,
            company.payment_methods,
            PaymentMethodORM,
        )

        #
        # Temporary social link handling.
        #

        cls._sync_collection(
            orm.social_links,
            {
                f"{platform}|{url}"
                for platform, url
                in company.social_links.items()
            },
            SocialLinkORM,
        )
