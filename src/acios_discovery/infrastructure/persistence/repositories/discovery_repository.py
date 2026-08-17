from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.domain.discovery.record import (
    DiscoveryRecord,
)
from acios_discovery.domain.discovery.repository import (
    DiscoveryRepository,
)
from acios_discovery.infrastructure.persistence.mappers.discovery_mapper import (
    DiscoveryMapper,
)
from acios_discovery.infrastructure.persistence.orm.discovery import (
    DiscoveryORM,
)


class SqlAlchemyDiscoveryRepository(
    DiscoveryRepository,
):
    """
    SQLAlchemy implementation of the DiscoveryRepository.

    The repository operates on an externally supplied AsyncSession
    so multiple repositories can participate in the same transaction.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    

    

    async def save(
        self,
        record: DiscoveryRecord,
    ) -> None:
        """
        Persist a discovery record.

        A discovery is uniquely identified by:
            source + detail_url

        If the discovery already exists, update its discovery data
        instead of creating a duplicate.

        Resolution state is intentionally preserved when an existing
        discovery is updated.
        """

        values = DiscoveryMapper.to_orm(
            record,
        )

        insert_values = {
            column.name: getattr(values, column.name)
            for column in DiscoveryORM.__table__.columns
            if column.name != "id"
        }

        # Core INSERT does not apply the ORM Python-side default when
        # resolution_status is explicitly supplied as None.
        insert_values["resolution_status"] = "PENDING"

        stmt = (
            insert(
                DiscoveryORM,
            )
            .values(
                insert_values,
            )
            .on_conflict_do_update(
                constraint="uq_discoveries_source_detail_url",
                set_={
                    "business_name": insert_values["business_name"],
                    "address": insert_values["address"],
                    "description": insert_values["description"],
                    "phone_numbers": insert_values["phone_numbers"],
                    "email": insert_values["email"],
                    "website": insert_values["website"],
                    "social_links": insert_values["social_links"],
                    "product_types": insert_values["product_types"],
                    "payment_methods": insert_values["payment_methods"],
                    "year_founded": insert_values["year_founded"],
                    "employee_count": insert_values["employee_count"],
                    "business_locations": insert_values[
                        "business_locations"
                    ],
                    "country": insert_values["country"],
                    "state": insert_values["state"],
                    "city": insert_values["city"],
                    "root": insert_values["root"],
                    "industry": insert_values["industry"],
                    "sector": insert_values["sector"],
                    "category": insert_values["category"],
                    "subcategory": insert_values["subcategory"],
                    "listing_url": insert_values["listing_url"],
                    "page_number": insert_values["page_number"],
                    "discovered_at": insert_values["discovered_at"],
                },
            )
        )

        await self._session.execute(
            stmt,
        )    


    async def update(
        self,
        record: DiscoveryRecord,
    ) -> None:
        """
        Update an existing discovery.

        A discovery is identified by its source and business name.
        """

        stmt = (
            select(DiscoveryORM)
            .where(
                DiscoveryORM.source
                == str(record.company.source),
                DiscoveryORM.detail_url
                == record.company.detail_url,
            )
        )

        result = await self._session.execute(
            stmt,
        )

        orm = result.scalar_one_or_none()

        if orm is None:
            raise ValueError(
                "Discovery record does not exist: "
                f"{record.company.business_name}"
            )

        DiscoveryMapper.update_orm(
            orm,
            record,
        )



    async def resolve(
        self,
        record: DiscoveryRecord,
        company_id: CompanyId,
        resolved_at: datetime,
    ) -> None:
        """
        Associate an existing discovery with its canonical company.
        """

        stmt = (
            select(DiscoveryORM)
            .where(
                DiscoveryORM.source
                == str(record.company.source),
                DiscoveryORM.detail_url
                == record.company.detail_url,
            )
        )

        result = await self._session.execute(
            stmt,
        )

        orm = result.scalar_one_or_none()

        if orm is None:
            raise ValueError(
                "Discovery does not exist: "
                f"{record.company.business_name}",
            )

        orm.resolved_company_id = company_id.value
        orm.resolution_status = "RESOLVED"
        orm.resolved_at = resolved_at




    async def exists(
        self,
        record: DiscoveryRecord,
    ) -> bool:
        stmt = (
            select(DiscoveryORM.id)
            .where(
                DiscoveryORM.source
                == str(record.company.source),
                DiscoveryORM.detail_url
                == record.company.detail_url,
            )
        )

        result = await self._session.execute(
            stmt,
        )

        return result.scalar_one_or_none() is not None

    async def list_all(
        self,
    ) -> list[DiscoveryRecord]:
        stmt = (
            select(DiscoveryORM)
            .order_by(
                DiscoveryORM.id,
            )
        )

        result = await self._session.execute(
            stmt,
        )

        rows = result.scalars().all()

        return [
            DiscoveryMapper.to_domain(row)
            for row in rows
        ]

    async def count(
        self,
    ) -> int:
        
        stmt = (
            select(
                func.count(),
            )
            .select_from(
                DiscoveryORM,
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
        stmt = delete(
            DiscoveryORM,
        )

        await self._session.execute(
            stmt,
        )
