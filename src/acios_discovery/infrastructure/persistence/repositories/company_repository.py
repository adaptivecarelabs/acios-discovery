from __future__ import annotations

from urllib.parse import urlparse

from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from acios_discovery.application.normalization.canonical_business_name import (
    CanonicalBusinessNameNormalizer,
)
from acios_discovery.application.normalization.company_lookup import (
    normalize_company_alias,
    normalize_company_email,
    normalize_company_name,
    normalize_company_phone,
    normalize_company_website,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.domain.company.company_repository import (
    CompanyRepository,
)
from acios_discovery.infrastructure.persistence.mappers.company_mapper import (
    CompanyMapper,
)
from acios_discovery.infrastructure.persistence.orm.company import (
    CompanyORM,
)
from acios_discovery.infrastructure.persistence.orm.company_alias import (
    CompanyAliasORM,
)
from acios_discovery.infrastructure.persistence.orm.email import (
    EmailORM,
)
from acios_discovery.infrastructure.persistence.orm.phone_number import (
    PhoneNumberORM,
)
from acios_discovery.infrastructure.persistence.orm.website import (
    WebsiteORM,
)


class SqlAlchemyCompanyRepository(
    CompanyRepository,
):
    """
    SQLAlchemy implementation
    of CompanyRepository.
    """

    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session
        self._normalizer = CanonicalBusinessNameNormalizer()


    def _normalize_website(
        self,
        website: str,
    ) -> str:

        if not website:
            return ""

        if "://" not in website:
            website = "https://" + website

        domain = urlparse(
            website,
        ).netloc.lower()

        return domain.removeprefix(
            "www."
        )



    def _company_load_options(self):
        """
        Explicitly eager-load all Company aggregate collections.

        The domain mapper accesses these relationships while converting
        CompanyORM into the domain Company object. Explicit selectinload()
        prevents SQLAlchemy async lazy-loading / MissingGreenlet errors.
        """

        return (
            selectinload(CompanyORM.aliases),
            selectinload(CompanyORM.addresses),
            selectinload(CompanyORM.categories),
            selectinload(CompanyORM.cities),
            selectinload(CompanyORM.emails),
            selectinload(CompanyORM.payment_methods),
            selectinload(CompanyORM.phone_numbers),
            selectinload(CompanyORM.product_types),
            selectinload(CompanyORM.social_links),
            selectinload(CompanyORM.sources),
            selectinload(CompanyORM.states),
            selectinload(CompanyORM.websites),
        )

    
    #
    # CRUD
    #

    async def add(
        self,
        company: Company,
    ) -> None:

        orm = CompanyMapper.to_orm(company)

        self._session.add(orm)


    async def get(
        self,
        company_id: CompanyId,
    ) -> Company | None:

        stmt = (
            select(CompanyORM)
            .options(
                *self._company_load_options(),
            )
            .where(
                CompanyORM.id == company_id.value,
            )
        )

        result = await self._session.execute(stmt)

        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return CompanyMapper.to_domain(orm)
    

    async def list_all(
        self,
    ) -> list[Company]:

        stmt = (
            select(CompanyORM)
            .options(
                *self._company_load_options(),
            )
        )

        result = await self._session.execute(stmt)

        return [
            CompanyMapper.to_domain(company)
            for company in result.scalars().all()
        ]
    

    async def count(
        self,
    ) -> int:

        stmt = (
            select(
                func.count(),
            )
            .select_from(
                CompanyORM,
            )
        )

        result = await self._session.execute(stmt)

        return result.scalar_one()
    

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

        result = await self._session.execute(stmt)

        orm = result.scalar_one_or_none()

        if orm is None:
            raise ValueError(
                f"Company not found: {company.id.value}",
            )

        CompanyMapper.update_orm(
            orm,
            company,
        )

    #
    # LOOKUPS
    #

    async def find_by_name(
        self,
        canonical_name: str,
    ) -> Company | None:

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

        result = await self._session.execute(stmt)

        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return CompanyMapper.to_domain(orm)

    

    async def find_by_alias(
        self,
        alias: str,
    ) -> Company | None:

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

        result = await self._session.execute(stmt)

        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return CompanyMapper.to_domain(orm)

    

    async def find_by_phone(
        self,
        phone: str,
    ) -> Company | None:

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

        result = await self._session.execute(stmt)

        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return CompanyMapper.to_domain(orm)


    
    async def find_by_email(
        self,
        email: str,
    ) -> Company | None:

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

        result = await self._session.execute(stmt)

        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return CompanyMapper.to_domain(orm)

    

    async def find_by_website(
        self,
        website: str,
    ) -> Company | None:

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

        result = await self._session.execute(stmt)

        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return CompanyMapper.to_domain(orm)

