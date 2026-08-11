from unittest.mock import AsyncMock

import pytest

from acios_discovery.application.company.company_factory import (
    CompanyFactory,
)
from acios_discovery.application.persistence.discovery_persistence_pipeline import (
    DiscoveryPersistencePipeline,
)
from acios_discovery.application.resolution.resolution_result import (
    ResolutionResult,
)
from acios_discovery.domain.discovery.context import DiscoveryContext
from acios_discovery.domain.discovery.models import RawDiscovery
from acios_discovery.domain.discovery.record import DiscoveryRecord
from acios_discovery.domain.sources import Source
from acios_discovery.application.company.sequential_company_id_allocator import (
    SequentialCompanyIdAllocator,
)




def make_record() -> DiscoveryRecord:
    return DiscoveryRecord(
        context=DiscoveryContext(
            source=Source.FINELIB,
            state="Lagos",
            city="Yaba",
            category="restaurants",
            listing_url="https://example.com/restaurants",
        ),
        company=RawDiscovery(
            source=Source.FINELIB,
            business_name="Test Company",
            detail_url="https://example.com/company/test",
        ),
    )


@pytest.mark.asyncio
async def test_pipeline_saves_new_discovery() -> None:
    discovery_repository = AsyncMock()

    discovery_repository.exists.return_value = False

    company_repository = AsyncMock()

    resolution_service = AsyncMock()

    company_factory = CompanyFactory(id_allocator=SequentialCompanyIdAllocator(),)

    resolution_service.resolve.return_value = ResolutionResult(
        company = None,
        confidence = 0.0,
        duplicate = False,
    )

    pipeline = DiscoveryPersistencePipeline(
        discovery_repository=discovery_repository,
        company_repository=company_repository,
        resolution_service=resolution_service,
        company_factory=company_factory,
    )

    record = make_record()

    await pipeline.persist(
        sequence=1,
        discovery=record,
    )

    discovery_repository.exists.assert_awaited_once_with(
        record,
    )

    discovery_repository.save.assert_awaited_once_with(
        record,
    )


@pytest.mark.asyncio
async def test_pipeline_skips_existing_discovery() -> None:
    discovery_repository = AsyncMock()

    discovery_repository.exists.return_value = True

    company_repository = AsyncMock()

    resolution_service = AsyncMock()

    company_factory = CompanyFactory(id_allocator=SequentialCompanyIdAllocator(),)

    pipeline = DiscoveryPersistencePipeline(
        discovery_repository=discovery_repository,
        company_repository=company_repository,
        resolution_service=resolution_service,
        company_factory=company_factory,
    )

    record = make_record()

    await pipeline.persist(
        sequence=1,
        discovery=record,
    )

    discovery_repository.exists.assert_awaited_once_with(
        record,
    )

    discovery_repository.save.assert_not_awaited()



@pytest.mark.asyncio
async def test_pipeline_resolves_saved_discovery() -> None:
    discovery_repository = AsyncMock()

    discovery_repository.exists.return_value = False

    company_repository = AsyncMock()

    resolution_service = AsyncMock()

    resolution_service.resolve.return_value = ResolutionResult(
        company=None,
        confidence=0.0,
        duplicate=False,
    )

    company_factory = CompanyFactory(id_allocator=SequentialCompanyIdAllocator(),)

    pipeline = DiscoveryPersistencePipeline(
        discovery_repository=discovery_repository,
        company_repository=company_repository,
        resolution_service=resolution_service,
        company_factory=company_factory,
    )

    record = make_record()

    await pipeline.persist(
        sequence=1,
        discovery=record,
    )

    resolution_service.resolve.assert_awaited_once_with(
        record.company,
    )



@pytest.mark.asyncio
async def test_pipeline_creates_new_company() -> None:
    discovery_repository = AsyncMock()

    discovery_repository.exists.return_value = False

    company_repository = AsyncMock()

    resolution_service = AsyncMock()

    resolution_service.resolve.return_value = ResolutionResult(
        company=None,
        confidence=0.0,
        duplicate=False,
    )

    company_factory = CompanyFactory(id_allocator=SequentialCompanyIdAllocator(),)

    pipeline = DiscoveryPersistencePipeline(
        discovery_repository=discovery_repository,
        company_repository=company_repository,
        resolution_service=resolution_service,
        company_factory=company_factory,
    )

    record = make_record()

    await pipeline.persist(
        sequence=1,
        discovery=record,
    )

    company_repository.add.assert_awaited_once()


@pytest.mark.asyncio
async def test_pipeline_updates_existing_company() -> None:
    discovery_repository = AsyncMock()

    discovery_repository.exists.return_value = False

    company_repository = AsyncMock()

    resolution_service = AsyncMock()

    existing_company = await CompanyFactory(id_allocator=SequentialCompanyIdAllocator(),).create(
        discovery=make_record().company,
    )

    resolution_service.resolve.return_value = ResolutionResult(
        company=existing_company,
        confidence=95.0,
        duplicate=True,
    )

    company_factory = CompanyFactory(id_allocator=SequentialCompanyIdAllocator(),)

    pipeline = DiscoveryPersistencePipeline(
        discovery_repository=discovery_repository,
        company_repository=company_repository,
        resolution_service=resolution_service,
        company_factory=company_factory,
    )

    record = make_record()

    await pipeline.persist(
        sequence=2,
        discovery=record,
    )

    company_repository.update.assert_awaited_once_with(
        existing_company,
    )
