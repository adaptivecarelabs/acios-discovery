from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

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
from acios_discovery.infrastructure.persistence.repositories.discovery_repository import (
    SqlAlchemyDiscoveryRepository,
)


def make_record(
    *,
    name: str = "Test Company",
    address: str = "1 Test Street, Lagos",
    page_number: int = 1,
) -> DiscoveryRecord:

    return DiscoveryRecord(
        company=RawDiscovery(
            source=Source.FINELIB.value,
            business_name=name,
            detail_url=(
                "https://www.finelib.com/"
                "listing/test-company/12345/"
            ),
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
    test_engine: AsyncEngine,
) -> SqlAlchemyDiscoveryRepository:

    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return SqlAlchemyDiscoveryRepository(
        session_factory=session_factory,
    )


async def test_save_and_count(
    test_engine: AsyncEngine,
) -> None:

    repository = make_repository(
        test_engine,
    )

    record = make_record()

    assert await repository.count() == 0

    await repository.save(record)

    assert await repository.count() == 1


async def test_save_and_exists(
    test_engine: AsyncEngine,
) -> None:

    repository = make_repository(
        test_engine,
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
    test_engine: AsyncEngine,
) -> None:

    repository = make_repository(
        test_engine,
    )

    first = make_record(
        name="Company One",
    )

    second = make_record(
        name="Company Two",
    )

    await repository.save(first)
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
    test_engine: AsyncEngine,
) -> None:

    repository = make_repository(
        test_engine,
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
    test_engine: AsyncEngine,
) -> None:

    repository = make_repository(
        test_engine,
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
    test_engine: AsyncEngine,
) -> None:

    repository = make_repository(
        test_engine,
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
