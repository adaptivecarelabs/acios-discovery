import pytest

from acios_discovery.application.company.company_factory import (
    CompanyFactory,
)
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
from acios_discovery.domain.discovery.models import (
    RawDiscovery,
)
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.repositories.in_memory_company_repository import (
    InMemoryCompanyRepository,
)
from acios_discovery.application.company.sequential_company_id_allocator import (
    SequentialCompanyIdAllocator,
)




def make_discovery(
    name: str,
    phone: str | None = None,
) -> RawDiscovery:

    return RawDiscovery(
        source=Source.FINELIB,
        business_name=name,
        phone_numbers=[phone] if phone else [],
    )


@pytest.mark.asyncio
async def test_register_creates_company():

    company_repository = InMemoryCompanyRepository()

    resolution = EntityResolutionService(
        repository=company_repository,
        engine=EntityResolutionEngine(),
    )

    service = DiscoveryCompanyRegistryService(
        repository=company_repository,
        resolution_service=resolution,
        factory=CompanyFactory(id_allocator=SequentialCompanyIdAllocator(),),
        merge_service=CompanyMergeService(),
    )

    company = await service.register(
        sequence=1,
        discovery=make_discovery(
            "Drugstoc",
        ),
    )

    assert company.canonical_name == "DRUGSTOC"

    assert await company_repository.count() == 1


@pytest.mark.asyncio
async def test_register_merges_duplicate():

    company_repository = InMemoryCompanyRepository()

    factory = CompanyFactory(id_allocator=SequentialCompanyIdAllocator(),)

    existing = await factory.create(
        discovery=make_discovery(
            "Drugstoc",
            phone="08030000000",
        ),
    )

    await company_repository.add(
        existing,
    )

    resolution = EntityResolutionService(
        repository=company_repository,
        engine=EntityResolutionEngine(),
    )

    service = DiscoveryCompanyRegistryService(
        repository=company_repository,
        resolution_service=resolution,
        factory=CompanyFactory(id_allocator=SequentialCompanyIdAllocator(),),
        merge_service=CompanyMergeService(),
    )

    company = await service.register(
        sequence=1,
        discovery=make_discovery(
            "Drugstoc Ltd",
            phone="08030000000",
        ),
    )

    assert company.id == existing.id

    assert any(
        alias.upper() == "DRUGSTOC LTD"
        for alias in company.aliases
    )

    assert "08030000000" in company.phone_numbers
