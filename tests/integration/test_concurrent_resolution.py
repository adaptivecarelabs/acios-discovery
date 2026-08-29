from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.application.company.company_factory import CompanyFactory
from acios_discovery.application.company.company_merge_service import (
    CompanyMergeService,
)
from acios_discovery.application.company.discovery_company_registry_service import (
    DiscoveryCompanyRegistryService,
)
from acios_discovery.application.resolution.entity_resolution_engine import (
    EntityResolutionEngine,
)
from acios_discovery.application.resolution.entity_resolution_service import (
    EntityResolutionService,
)
from acios_discovery.domain.discovery.context import DiscoveryContext
from acios_discovery.domain.discovery.models import RawDiscovery
from acios_discovery.domain.discovery.record import DiscoveryRecord
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.persistence.orm.company import CompanyORM
from acios_discovery.infrastructure.persistence.repositories.company_match_repository import (
    SqlAlchemyCompanyMatchRepository,
)
from acios_discovery.infrastructure.persistence.repositories.discovery_repository import (
    SqlAlchemyDiscoveryRepository,
)
from acios_discovery.infrastructure.persistence.repositories.sequence_company_id_allocator import (
    SequenceCompanyIdAllocator,
)
from acios_discovery.infrastructure.persistence.unit_of_work import (
    SqlAlchemyUnitOfWork,
)


def make_record(
    detail_url: str,
) -> DiscoveryRecord:
    return DiscoveryRecord(
        context=DiscoveryContext(
            source=Source.FINELIB,
            state="Lagos",
            city="Lagos",
            category="Healthcare",
            listing_url="https://www.finelib.com/cities/lagos/health",
        ),
        company=RawDiscovery(
            source=Source.FINELIB,
            business_name="Concurrent Resolution Test Group",
            detail_url=detail_url,
            phone_numbers=["08030000000"],
        ),
    )


async def register_via_own_session(
    session_factory,
    record: DiscoveryRecord,
) -> None:
    """
    Save and register one discovery record on its own,
    independent session/transaction — simulating one
    crawl worker.
    """

    async with session_factory() as session:

        discovery_repository = SqlAlchemyDiscoveryRepository(
            session,
        )

        await discovery_repository.save(
            record,
        )

        await session.commit()

    async with session_factory() as session:

        unit_of_work = SqlAlchemyUnitOfWork(
            session,
        )

        match_repository = SqlAlchemyCompanyMatchRepository(
            session,
        )

        resolution_service = EntityResolutionService(
            repository=match_repository,
            engine=EntityResolutionEngine(),
        )

        registry = DiscoveryCompanyRegistryService(
            unit_of_work=unit_of_work,
            resolution_service=resolution_service,
            factory=CompanyFactory(
                id_allocator=SequenceCompanyIdAllocator(session),
            ),
            merge_service=CompanyMergeService(),
        )

        await registry.register(
            record=record,
        )


@pytest.mark.asyncio
async def test_concurrent_discoveries_of_same_company_do_not_duplicate(
    db_session: AsyncSession,
    test_session_factory,
) -> None:

    record_one = make_record(
        "https://www.finelib.com/listing/concurrent-test/1/",
    )

    record_two = make_record(
        "https://www.finelib.com/listing/concurrent-test/2/",
    )

    await asyncio.gather(
        register_via_own_session(
            test_session_factory,
            record_one,
        ),
        register_via_own_session(
            test_session_factory,
            record_two,
        ),
    )

    count = await db_session.scalar(
        select(func.count()).select_from(CompanyORM).where(
            CompanyORM.canonical_name == "CONCURRENT RESOLUTION TEST GROUP",
        )
    )

    assert count == 1
