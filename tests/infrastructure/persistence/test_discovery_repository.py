from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.domain.discovery.context import (
    DiscoveryContext,
)
from acios_discovery.domain.discovery.models import (
    RawDiscovery,
)
from acios_discovery.domain.discovery.record import (
    DiscoveryRecord,
)
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.persistence.orm.discovery import (
    DiscoveryORM,
)
from acios_discovery.infrastructure.persistence.repositories.company_repository import (
    SqlAlchemyCompanyRepository,
)
from acios_discovery.infrastructure.persistence.repositories.discovery_repository import (
    SqlAlchemyDiscoveryRepository,
)


def make_record(
    *,
    name: str = "Test Company",
    address: str = "1 Test Street, Lagos",
    page_number: int = 1,
    detail_url: str | None = None,
) -> DiscoveryRecord:

    if detail_url is None:
        slug = (
            name.lower()
            .replace(" ", "-")
            .replace(",", "")
        )

        detail_url = (
            "https://www.finelib.com/"
            f"listing/{slug}/12345/"
        )

    return DiscoveryRecord(
        company=RawDiscovery(
            source=Source.FINELIB.value,
            business_name=name,
            detail_url=detail_url,
            address=address,
            description="A test discovery.",
            phone_numbers=[
                "0801 234 5678",
            ],
            email="test@example.com",
            website="https://example.com",
            social_links={
                "facebook": (
                    "https://facebook.com/test"
                ),
            },
            product_types=[
                "Restaurant",
            ],
            payment_methods=[
                "Cash",
                "Card",
            ],
            year_founded=2020,
            employee_count="10-20",
            business_locations=1,
            category="Food",
            city="Lagos",
            state="Lagos",
        ),
        context=DiscoveryContext(
            source=Source.FINELIB,
            country="Nigeria",
            state="Lagos",
            city="Lagos",
            root="business",
            industry="Food",
            sector=None,
            category="Food",
            subcategory="Restaurants",
            listing_url=(
                "https://www.finelib.com/"
                "cities/lagos/business/food/restaurants"
            ),
            page_number=page_number,
        ),
    )

def make_repository(
    db_session: AsyncSession,
) -> SqlAlchemyDiscoveryRepository:

    return SqlAlchemyDiscoveryRepository(
        db_session,
    )


async def test_save_and_count(
    db_session: AsyncSession,
) -> None:

    repository = make_repository(
        db_session,
    )

    record = make_record()

    assert await repository.count() == 0

    await repository.save(record)

    assert await repository.count() == 1


async def test_save_and_exists(
    db_session: AsyncSession,
) -> None:

    repository = make_repository(
        db_session,
    )

    record = make_record()

    assert (
        await repository.exists(record)
        is False
    )

    await repository.save(record)

    assert (
        await repository.exists(record)
        is True
    )


async def test_list_all(
    db_session: AsyncSession,
) -> None:

    repository = make_repository(
        db_session,
    )

    first = make_record(
        name="Company One",
        detail_url=(
        "https://www.finelib.com/"
        "listing/company-one/12345/"
         ),
    )

    second = make_record(
        name="Company Two",
        detail_url=(
        "https://www.finelib.com/"
        "listing/company-two/67890/"
        ),
    )

    await repository.save(first)
    print("FIRST NAME:", first.company.business_name)
    print("FIRST SOURCE:", first.company.source)
    print("FIRST URL:", first.company.detail_url)

    print("SECOND NAME:", second.company.business_name)
    print("SECOND SOURCE:", second.company.source)
    print("SECOND URL:", second.company.detail_url)

    await repository.save(second)

    records = await repository.list_all()

    assert len(records) == 2

    names = {
        record.company.business_name
        for record in records
    }

    assert names == {
        "Company One",
        "Company Two",
    }


async def test_update(
    db_session: AsyncSession,
) -> None:

    repository = make_repository(
        db_session,
    )

    record = make_record()

    await repository.save(record)

    updated = make_record(
        address="99 New Address, Lagos",
    )

    await repository.update(updated)

    records = await repository.list_all()

    assert len(records) == 1

    stored = records[0]

    assert (
        stored.company.business_name
        == "Test Company"
    )

    assert (
        stored.company.address
        == "99 New Address, Lagos"
    )


async def test_update_missing_record_raises(
    db_session: AsyncSession,
) -> None:

    repository = make_repository(
        db_session,
    )

    record = make_record()

    try:
        await repository.update(record)
    except ValueError as exc:
        assert "Test Company" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


async def test_clear(
    db_session: AsyncSession,
) -> None:

    repository = make_repository(
        db_session,
    )

    await repository.save(
        make_record(
            name="Company One",
        )
    )

    await repository.save(
        make_record(
            name="Company Two",
        )
    )

    assert await repository.count() == 2

    await repository.clear()

    assert await repository.count() == 0


@pytest.mark.asyncio
async def test_discovery_round_trip(
    db_session,
    discovery_record,
):
    repository = SqlAlchemyDiscoveryRepository(
        db_session,
    )

    await repository.save(
        discovery_record,
    )

    await db_session.commit()

    records = await repository.list_all()

    assert len(records) == 1

    saved = records[0]

    assert (
        saved.company.business_name
        == discovery_record.company.business_name
    )

    assert (
        saved.company.detail_url
        == discovery_record.company.detail_url
    )

    assert (
        saved.context.city
        == discovery_record.context.city
    )


@pytest.mark.asyncio
async def test_saving_same_discovery_does_not_create_duplicate(
    db_session,
    discovery_record,
):
    repository = SqlAlchemyDiscoveryRepository(
        db_session,
    )

    await repository.save(
        discovery_record,
    )

    await db_session.flush()

    await repository.save(
        discovery_record,
    )

    await db_session.flush()

    count = await repository.count()

    assert count == 1



@pytest.mark.asyncio
async def test_resolve_updates_existing_discovery(
    db_session: AsyncSession,
    discovery_record: DiscoveryRecord,
) -> None:
    discovery_repository = SqlAlchemyDiscoveryRepository(
        db_session,
    )

    company_repository = SqlAlchemyCompanyRepository(
        db_session,
    )

    await discovery_repository.save(
        discovery_record,
    )

    company_id = CompanyId(
        "ACL-COM-00000001",
    )

    company = Company(
        id=company_id,
        canonical_name="Drugstoc EHub Ltd",
    )

    await company_repository.add(
        company,
    )

    await db_session.flush()

    resolved_at = datetime.now(UTC)

    await discovery_repository.resolve(
        discovery_record,
        company_id,
        resolved_at,
    )

    await db_session.flush()

    stmt = select(
        DiscoveryORM,
    ).where(
        DiscoveryORM.source
        == str(discovery_record.company.source),
        DiscoveryORM.detail_url
        == discovery_record.company.detail_url,
    )

    result = await db_session.execute(
        stmt,
    )

    row = result.scalar_one()

    assert row.resolved_company_id == (
        "ACL-COM-00000001"
    )

    assert row.resolution_status == (
        "RESOLVED"
    )

    assert row.resolved_at is not None

    assert row.resolved_at == resolved_at
