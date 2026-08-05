from __future__ import annotations

from urllib.parse import urlparse

from acios_discovery.application.normalization.canonical_business_name import (
    CanonicalBusinessNameNormalizer,
)
from acios_discovery.application.resolution.field_similarity import (
    normalize_phone,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.domain.company.company_repository import (
    CompanyRepository,
)


class InMemoryCompanyRepository(
    CompanyRepository,
):

    def __init__(self) -> None:

        self._companies: dict[
            CompanyId,
            Company,
        ] = {}

        #
        # Lookup indexes
        #

        self._name_index: dict[str, CompanyId] = {}

        self._alias_index: dict[str, CompanyId] = {}

        self._phone_index: dict[str, CompanyId] = {}

        self._email_index: dict[str, CompanyId] = {}

        self._website_index: dict[str, CompanyId] = {}

        self._normalizer = CanonicalBusinessNameNormalizer()


    def _index_company(
        self,
        company: Company,
    ) -> None:
        """
        Adds every searchable value into the lookup indexes.
        """

        #
        # Canonical name
        #

        canonical = self._normalizer.normalize(
            company.canonical_name,
        )

        self._name_index[
            canonical
        ] = company.id

        #
        # Aliases
        #

        for alias in company.aliases:

            self._alias_index[
                self._normalizer.normalize(alias)
            ] = company.id

        #
        # Phones
        #

        for phone in company.phone_numbers:

            self._phone_index[
                normalize_phone(phone)
            ] = company.id

        #
        # Emails
        #

        for email in company.emails:

            self._email_index[
                email.lower()
            ] = company.id

        #
        # Websites
        #

        for website in company.websites:

            self._website_index[
                self._normalize_website(
                    website,
                )
            ]= company.id

    def _normalize_website(
        self,
        website: str,
    ) -> str:

        if not website:
            return ""

        #
        # Allow plain domains too
        #
        if "://" not in website:
            website = "https://" + website

        domain = urlparse(
            website,
        ).netloc.lower()

        return domain.removeprefix(
            "www."
        )
    

    async def add(
        self,
        company: Company,
    ) -> None:

        self._companies[
            company.id
        ]= company

        self._index_company(
            company,
        )


    async def get(
        self,
        company_id: CompanyId,
    ) -> Company | None:

        return self._companies.get(
            company_id,
        )

    async def list_all(
        self,
    ) -> list[Company]:

        return list(
            self._companies.values(),
        )

    async def count(
        self,
    ) -> int:

        return len(
            self._companies,
        )

    async def update(
        self,
        company: Company,
    ) -> None:

        self._companies[
            company.id
        ] = company


    async def find_by_name(
        self,
        canonical_name: str,
    ) -> Company | None:

        normalized = self._normalizer.normalize(
            canonical_name,
        )

        #
        # Canonical name lookup
        #

        company_id = self._name_index.get(
            normalized,
        )

        if company_id is not None:

            return self._companies.get(
                company_id,
            )

        #
        # Alias lookup
        #

        company_id = self._alias_index.get(
            normalized,
        )

        if company_id is not None:

            return self._companies.get(
                company_id,
            )

        return None

    async def find_by_phone(
        self,
        phone: str,
    ) -> Company | None:

        company_id = self._phone_index.get(
            normalize_phone(
                phone,
            ),
        )

        if company_id is None:
            return None

        return self._companies.get(
            company_id,
        )

    async def find_by_email(
        self,
        email: str,
    ) -> Company | None:

        company_id = self._email_index.get(
            email.lower(),
        )

        if company_id is None:
            return None

        return self._companies.get(
            company_id,
        )

    async def find_by_website(
        self,
        website: str,
    ) -> Company | None:

        company_id = self._website_index.get(
            self._normalize_website(
                website,
            ),
        )

        if company_id is None:
            return None

        return self._companies.get(
            company_id,
        )
