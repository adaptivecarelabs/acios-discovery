from __future__ import annotations

from acios_discovery.application.normalization.company_lookup import (
    normalize_company_alias,
    normalize_company_email,
    normalize_company_name,
    normalize_company_phone,
    normalize_company_website,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_repository import (
    CompanyRepository,
)
from acios_discovery.domain.discovery.company_match_repository import (
    CompanyMatchRepository,
)
from acios_discovery.domain.discovery.models import RawDiscovery


class InMemoryCompanyMatchRepository(CompanyMatchRepository):
    """
    In-memory CompanyMatchRepository backed by a CompanyRepository.

    Test-only: scans the wrapped repository's full company list
    and filters using the same exact-match + geography rules the
    real SQL implementation applies at the query level. Bounding
    is irrelevant for small test fixtures; this exists so tests
    exercise the same candidate-selection *logic* the SQL
    implementation uses, not to be performant.
    """

    def __init__(
        self,
        company_repository: CompanyRepository,
    ) -> None:
        self._company_repository = company_repository

    async def candidates(
        self,
        discovery: RawDiscovery,
    ) -> list[Company]:

        companies = await self._company_repository.list_all()

        normalized_name = normalize_company_name(
            discovery.business_name,
        )

        normalized_phones = {
            normalize_company_phone(phone)
            for phone in discovery.phone_numbers
            if phone
        }

        normalized_email = (
            normalize_company_email(discovery.email)
            if discovery.email
            else None
        )

        normalized_website = (
            normalize_company_website(discovery.website)
            if discovery.website
            else None
        )

        matches: list[Company] = []

        for company in companies:

            if (
                normalize_company_name(company.canonical_name)
                == normalized_name
            ):
                matches.append(company)
                continue

            if any(
                normalize_company_alias(alias) == normalized_name
                for alias in company.aliases
            ):
                matches.append(company)
                continue

            if normalized_phones and any(
                normalize_company_phone(phone) in normalized_phones
                for phone in company.phone_numbers
            ):
                matches.append(company)
                continue

            if normalized_email and any(
                normalize_company_email(email) == normalized_email
                for email in company.emails
            ):
                matches.append(company)
                continue

            if normalized_website and any(
                normalize_company_website(website) == normalized_website
                for website in company.websites
            ):
                matches.append(company)
                continue

            if discovery.city and discovery.city in company.cities:
                matches.append(company)
                continue

            if discovery.state and discovery.state in company.states:
                matches.append(company)
                continue

        return matches
