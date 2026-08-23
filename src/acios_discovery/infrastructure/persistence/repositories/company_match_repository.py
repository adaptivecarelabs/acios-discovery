from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from acios_discovery.application.normalization.company_lookup import (
    normalize_company_email,
    normalize_company_name,
    normalize_company_phone,
    normalize_company_website,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.discovery.company_match_repository import (
    CompanyMatchRepository,
)
from acios_discovery.domain.discovery.models import RawDiscovery
from acios_discovery.infrastructure.persistence.mappers.company_mapper import (
    CompanyMapper,
)
from acios_discovery.infrastructure.persistence.orm import (
    CityORM,
    CompanyAliasORM,
    CompanyORM,
    EmailORM,
    PhoneNumberORM,
    StateORM,
    WebsiteORM,
)


class SqlAlchemyCompanyMatchRepository(CompanyMatchRepository):
    """
    SQLAlchemy implementation of CompanyMatchRepository.

    Builds one query with the exact-match signals (name, alias,
    phone, email, website) and the geography signals (city,
    state) OR'd together, so the database — not Python — does
    the bounding. See CompanyMatchRepository for the rationale.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    @staticmethod
    def _load_options():

        return (
            selectinload(CompanyORM.aliases),
            selectinload(CompanyORM.emails),
            selectinload(CompanyORM.websites),
            selectinload(CompanyORM.addresses),
            selectinload(CompanyORM.phone_numbers),
            selectinload(CompanyORM.social_links),
            selectinload(CompanyORM.product_types),
            selectinload(CompanyORM.payment_methods),
            selectinload(CompanyORM.categories),
            selectinload(CompanyORM.cities),
            selectinload(CompanyORM.states),
            selectinload(CompanyORM.sources),
            selectinload(CompanyORM.scalar_provenance_rows),
            selectinload(CompanyORM.set_provenance_rows),
        )

    async def candidates(
        self,
        discovery: RawDiscovery,
    ) -> list[Company]:

        normalized_name = normalize_company_name(
            discovery.business_name,
        )

        conditions = [
            CompanyORM.canonical_name_normalized == normalized_name,
            CompanyORM.id.in_(
                select(CompanyAliasORM.company_id).where(
                    CompanyAliasORM.normalized_value == normalized_name,
                )
            ),
        ]

        normalized_phones = {
            normalize_company_phone(phone)
            for phone in discovery.phone_numbers
            if phone
        }

        if normalized_phones:
            conditions.append(
                CompanyORM.id.in_(
                    select(PhoneNumberORM.company_id).where(
                        PhoneNumberORM.normalized_value.in_(
                            normalized_phones,
                        )
                    )
                )
            )

        if discovery.email:
            conditions.append(
                CompanyORM.id.in_(
                    select(EmailORM.company_id).where(
                        EmailORM.normalized_value
                        == normalize_company_email(discovery.email),
                    )
                )
            )

        if discovery.website:
            conditions.append(
                CompanyORM.id.in_(
                    select(WebsiteORM.company_id).where(
                        WebsiteORM.normalized_value
                        == normalize_company_website(discovery.website),
                    )
                )
            )

        if discovery.city:
            conditions.append(
                CompanyORM.id.in_(
                    select(CityORM.company_id).where(
                        CityORM.value == discovery.city,
                    )
                )
            )

        if discovery.state:
            conditions.append(
                CompanyORM.id.in_(
                    select(StateORM.company_id).where(
                        StateORM.value == discovery.state,
                    )
                )
            )

        stmt = (
            select(CompanyORM)
            .options(*self._load_options())
            .where(or_(*conditions))
        )

        result = await self._session.execute(stmt)

        rows = result.unique().scalars().all()

        return [
            CompanyMapper.to_domain(row)
            for row in rows
        ]
