from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.application.discovery.discovery_persistence_service import (
    DiscoveryPersistenceService,
)
from acios_discovery.domain.discovery.context import DiscoveryContext
from acios_discovery.domain.discovery.models import RawDiscovery
from acios_discovery.domain.discovery.record import DiscoveryRecord
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.persistence.orm.discovery import (
    DiscoveryORM,
)
from acios_discovery.infrastructure.persistence.orm.outbox_event import (
    OutboxEventORM,
)
from acios_discovery.infrastructure.persistence.unit_of_work import (
    SqlAlchemyUnitOfWork,
)


def make_discovery_record() -> DiscoveryRecord:
    return DiscoveryRecord(
        context=DiscoveryContext(
            source=Source.FINELIB,
            country="Nigeria",
            state="Lagos",
            city="Lagos",
            category="Healthcare",
            listing_url="https://www.finelib.com/cities/lagos/health",
            page_number=1,
        ),
        company=RawDiscovery(
            source=Source.FINELIB,
            business_name="Persistence Boundary Test Company",
            detail_url=(
                "https://www.finelib.com/listing/"
                "persistence-boundary-test"
            ),
            address="Ikeja, Lagos",
            description="Persistence boundary integration test",
            phone_numbers=["08030000000"],
        ),
    )


class FailingOutboxRepository:
    async def add(
        self,
        message,
    ) -> None:
        raise RuntimeError(
            "Simulated outbox persistence failure"
        )


async def persist_record(
    db_session: AsyncSession,
    record: DiscoveryRecord,
) -> None:
    unit_of_work = SqlAlchemyUnitOfWork(
        db_session,
    )

    service = DiscoveryPersistenceService(
        unit_of_work=unit_of_work,
    )

    await service.persist(
        record,
    )


async def test_discovery_and_outbox_are_persisted_atomically(
    db_session: AsyncSession,
) -> None:
    record = make_discovery_record()

    await persist_record(
        db_session,
        record,
    )

    discovery_count = await db_session.scalar(
        select(
            func.count(),
        ).select_from(
            DiscoveryORM,
        ).where(
            DiscoveryORM.source
            == str(record.company.source),
            DiscoveryORM.detail_url
            == record.company.detail_url,
        )
    )

    outbox_count = await db_session.scalar(
        select(
            func.count(),
        ).select_from(
            OutboxEventORM,
        ).where(
            OutboxEventORM.event_type
            == "CompanyDiscoveredEvent",
        )
    )

    assert discovery_count == 1
    assert outbox_count == 1


async def test_duplicate_discovery_updates_existing_row(
    db_session: AsyncSession,
) -> None:
    record = make_discovery_record()

    await persist_record(
        db_session,
        record,
    )

    updated_record = DiscoveryRecord(
        context=record.context,
        company=RawDiscovery(
            source=record.company.source,
            business_name=record.company.business_name,
            detail_url=record.company.detail_url,
            address=record.company.address,
            description="Updated description",
            phone_numbers=record.company.phone_numbers,
            email=record.company.email,
            website=record.company.website,
            social_links=record.company.social_links,
            product_types=record.company.product_types,
            payment_methods=record.company.payment_methods,
            year_founded=record.company.year_founded,
            employee_count=record.company.employee_count,
            business_locations=record.company.business_locations,
            category=record.company.category,
            city=record.company.city,
            state=record.company.state,
            discovered_at=record.company.discovered_at,
        ),
    )

    await persist_record(
        db_session,
        updated_record,
    )

    discovery_rows = (
        await db_session.scalars(
            select(
                DiscoveryORM,
            ).where(
                DiscoveryORM.source
                == str(record.company.source),
                DiscoveryORM.detail_url
                == record.company.detail_url,
            )
        )
    ).all()

    assert len(discovery_rows) == 1
    assert (
        discovery_rows[0].description
        == "Updated description"
    )



async def test_discovery_is_rolled_back_when_outbox_persistence_fails(
    db_session: AsyncSession,
) -> None:
    record = make_discovery_record()

    unit_of_work = SqlAlchemyUnitOfWork(
        db_session,
    )

    unit_of_work.outbox_repository = (
        FailingOutboxRepository()
    )

    service = DiscoveryPersistenceService(
        unit_of_work=unit_of_work,
    )

    try:
        await service.persist(
            record,
        )
    except RuntimeError as exc:
        assert str(exc) == (
            "Simulated outbox persistence failure"
        )
    else:
        raise AssertionError(
            "Expected outbox persistence failure"
        )

    discovery_count = await db_session.scalar(
        select(
            func.count(),
        ).select_from(
            DiscoveryORM,
        ).where(
            DiscoveryORM.source
            == str(record.company.source),
            DiscoveryORM.detail_url
            == record.company.detail_url,
        )
    )

    outbox_count = await db_session.scalar(
        select(
            func.count(),
        ).select_from(
            OutboxEventORM,
        ).where(
            OutboxEventORM.event_type
            == "CompanyDiscoveredEvent",
        )
    )

    assert discovery_count == 0
    assert outbox_count == 0
