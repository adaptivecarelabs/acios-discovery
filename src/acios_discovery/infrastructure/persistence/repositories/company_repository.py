from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
from acios_discovery.infrastructure.persistence.mappers.company_mapper import (
    CompanyMapper,
)
from acios_discovery.infrastructure.persistence.orm import (
    CompanyAliasORM,
    CompanyORM,
    EmailORM,
    PhoneNumberORM,
    WebsiteORM,
)


class SqlAlchemyCompanyRepository(CompanyRepository):
    """
    SQLAlchemy implementation of CompanyRepository.

    The repository operates on an externally supplied AsyncSession
    so multiple repositories can participate in the same transaction.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    @staticmethod
    def _company_load_options():
        """
        Load the complete Company aggregate in one predictable query
        graph.
        """

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

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    async def add(
        self,
        company: Company,
    ) -> None:
        """
        Persist a new Company aggregate.
        """

        orm = CompanyMapper.to_orm(
            company,
        )

        self._session.add(
            orm,
        )

    async def update(
        self,
        company: Company,
    ) -> None:
        """
        Update an existing Company aggregate.
        """

        stmt = (
            select(CompanyORM)
            .options(
                *self._company_load_options(),
            )
            .where(
                CompanyORM.id == company.id.value,
            )
        )

        result = await self._session.execute(
            stmt,
        )

        orm = result.scalar_one_or_none()

        if orm is None:
            raise ValueError(
                f"Company does not exist: {company.id.value}",
            )

        CompanyMapper.update_orm(
            orm,
            company,
        )

    # ------------------------------------------------------------------
    # General queries
    # ------------------------------------------------------------------

    async def get(
        self,
        company_id,
    ) -> Company | None:
        """
        Retrieve a company by its domain ID.
        """

        stmt = (
            select(CompanyORM)
            .options(
                *self._company_load_options(),
            )
            .where(
                CompanyORM.id == company_id.value,
            )
        )

        result = await self._session.execute(
            stmt,
        )

        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return CompanyMapper.to_domain(
            orm,
        )

    async def list_all(
        self,
    ) -> list[Company]:
        """
        Return all registered companies.
        """

        stmt = (
            select(CompanyORM)
            .options(
                *self._company_load_options(),
            )
            .order_by(
                CompanyORM.id,
            )
        )

        result = await self._session.execute(
            stmt,
        )

        rows = result.scalars().all()

        return [
            CompanyMapper.to_domain(row)
            for row in rows
        ]

    async def count(
        self,
    ) -> int:
        """
        Return the number of registered companies.
        """

        stmt = (
            select(
                func.count(),
            )
            .select_from(
                CompanyORM,
            )
        )

        result = await self._session.execute(
            stmt,
        )

        return int(
            result.scalar_one(),
        )




    async def clear(
        self,
    ) -> None:
        """
        Delete all companies.
        """

        stmt = delete(
            CompanyORM,
        )

        await self._session.execute(
            stmt,
        )

    # ------------------------------------------------------------------
    # Identity resolution
    # ------------------------------------------------------------------

    async def find_by_name(
        self,
        canonical_name: str,
    ) -> Company | None:
        """
        Find a company by normalized canonical name.
        """

        normalized = normalize_company_name(
            canonical_name,
        )

        stmt = (
            select(CompanyORM)
            .options(
                *self._company_load_options(),
            )
            .where(
                CompanyORM.canonical_name_normalized
                == normalized,
            )
        )

        result = await self._session.execute(
            stmt,
        )

        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return CompanyMapper.to_domain(
            orm,
        )

    async def find_by_alias(
        self,
        alias: str,
    ) -> Company | None:
        """
        Find a company through one of its aliases.
        """

        normalized = normalize_company_alias(
            alias,
        )

        stmt = (
            select(CompanyORM)
            .join(
                CompanyAliasORM,
                CompanyAliasORM.company_id
                == CompanyORM.id,
            )
            .options(
                *self._company_load_options(),
            )
            .where(
                CompanyAliasORM.normalized_value
                == normalized,
            )
        )

        result = await self._session.execute(
            stmt,
        )

        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return CompanyMapper.to_domain(
            orm,
        )

    async def find_by_phone(
        self,
        phone: str,
    ) -> Company | None:
        """
        Find a company by normalized phone number.
        """

        normalized = normalize_company_phone(
            phone,
        )

        stmt = (
            select(CompanyORM)
            .join(
                PhoneNumberORM,
                PhoneNumberORM.company_id
                == CompanyORM.id,
            )
            .options(
                *self._company_load_options(),
            )
            .where(
                PhoneNumberORM.normalized_value
                == normalized,
            )
        )

        result = await self._session.execute(
            stmt,
        )

        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return CompanyMapper.to_domain(
            orm,
        )

    async def find_by_email(
        self,
        email: str,
    ) -> Company | None:
        """
        Find a company by normalized email address.
        """

        normalized = normalize_company_email(
            email,
        )

        stmt = (
            select(CompanyORM)
            .join(
                EmailORM,
                EmailORM.company_id
                == CompanyORM.id,
            )
            .options(
                *self._company_load_options(),
            )
            .where(
                EmailORM.normalized_value
                == normalized,
            )
        )

        result = await self._session.execute(
            stmt,
        )

        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return CompanyMapper.to_domain(
            orm,
        )

    async def find_by_website(
        self,
        website: str,
    ) -> Company | None:
        """
        Find a company by normalized website.
        """

        normalized = normalize_company_website(
            website,
        )

        stmt = (
            select(CompanyORM)
            .join(
                WebsiteORM,
                WebsiteORM.company_id
                == CompanyORM.id,
            )
            .options(
                *self._company_load_options(),
            )
            .where(
                WebsiteORM.normalized_value
                == normalized,
            )
        )

        result = await self._session.execute(
            stmt,
        )

        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return CompanyMapper.to_domain(
            orm,
        )
