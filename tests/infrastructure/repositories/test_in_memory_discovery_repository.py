import pytest

from acios_discovery.domain.discovery.record import DiscoveryRecord
from acios_discovery.infrastructure.persistence.in_memory_discovery_repository import (
    InMemoryDiscoveryRepository,
)


@pytest.mark.asyncio
async def test_repository_saves_record(
    sample_discovery_record: DiscoveryRecord,
) -> None:
    repository = InMemoryDiscoveryRepository()

    await repository.save(sample_discovery_record)

    records = await repository.list_all()

    assert len(records) == 1


@pytest.mark.asyncio
async def test_repository_detects_existing_record(
    sample_discovery_record: DiscoveryRecord,
) -> None:
    repository = InMemoryDiscoveryRepository()

    await repository.save(sample_discovery_record)

    assert await repository.exists(sample_discovery_record)


@pytest.mark.asyncio
async def test_repository_lists_records(
    sample_discovery_record: DiscoveryRecord,
) -> None:
    repository = InMemoryDiscoveryRepository()

    await repository.save(sample_discovery_record)

    records = await repository.list_all()

    assert records == [sample_discovery_record]


@pytest.mark.asyncio
async def test_repository_initially_empty() -> None:
    repository = InMemoryDiscoveryRepository()

    records = await repository.list_all()

    assert records == []
