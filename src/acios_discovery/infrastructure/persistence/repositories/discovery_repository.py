from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from acios_discovery.domain.discovery.record import (
    DiscoveryRecord,
)
from acios_discovery.domain.discovery.repository import (
    DiscoveryRepository,
)
from acios_discovery.infrastructure.persistence.database import (
    SessionFactory,
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

    The session factory is injectable so that persistence tests can
    provide an isolated test database session factory.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession]
        = SessionFactory,
    ) -> None:

        self._session_factory = session_factory

    async def save(
        self,
        record: DiscoveryRecord,
    ) -> None:

        async with self._session_factory() as session:

            orm = DiscoveryMapper.to_orm(
                record,
            )

            session.add(orm)

            await session.commit()

    async def update(
        self,
        record: DiscoveryRecord,
    ) -> None:
        """
        Update an existing discovery.

        A discovery is identified by its source and business name.
        """

        async with self._session_factory() as session:

            stmt = select(
                DiscoveryORM,
            ).where(
                DiscoveryORM.source
                == str(record.company.source),
                DiscoveryORM.business_name
                == record.company.business_name,
            )

            result = await session.execute(stmt)

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

            await session.commit()

    async def exists(
        self,
        record: DiscoveryRecord,
    ) -> bool:

        async with self._session_factory() as session:

            stmt = select(
                DiscoveryORM.id,
            ).where(
                DiscoveryORM.source
                == str(record.company.source),
                DiscoveryORM.business_name
                == record.company.business_name,
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none() is not None

    async def list_all(
        self,
    ) -> list[DiscoveryRecord]:

        async with self._session_factory() as session:

            stmt = select(
                DiscoveryORM,
            ).order_by(
                DiscoveryORM.id,
            )

            result = await session.execute(stmt)

            rows = result.scalars().all()

            return [
                DiscoveryMapper.to_domain(row)
                for row in rows
            ]

    async def count(
        self,
    ) -> int:

        async with self._session_factory() as session:

            stmt = select(
                DiscoveryORM,
            )

            result = await session.execute(stmt)

            return len(
                result.scalars().all()
            )

    async def clear(
        self,
    ) -> None:

        async with self._session_factory() as session:

            stmt = delete(
                DiscoveryORM,
            )

            await session.execute(stmt)

            await session.commit()
