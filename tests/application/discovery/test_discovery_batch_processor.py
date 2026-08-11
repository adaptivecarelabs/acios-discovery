import pytest

from acios_discovery.application.company.company_factory import CompanyFactory
from acios_discovery.application.company.company_merge_service import CompanyMergeService
from acios_discovery.application.company.discovery_company_registry_service import (
    DiscoveryCompanyRegistryService,
)
from acios_discovery.application.discovery.discovery_batch_processor import (
    DiscoveryBatchProcessor,
)
from acios_discovery.application.discovery.discovery_processor import (
    DiscoveryProcessor,
)
from acios_discovery.application.resolution.entity_resolution_engine import (
    EntityResolutionEngine,
)
from acios_discovery.application.resolution.entity_resolution_service import (
    EntityResolutionService,
)
from acios_discovery.domain.discovery.models import RawDiscovery
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.repositories.in_memory_company_match_repository import (
    InMemoryCompanyMatchRepository,
)
from acios_discovery.infrastructure.repositories.in_memory_company_repository import (
    InMemoryCompanyRepository,
)
from acios_discovery.application.company.sequential_company_id_allocator import (
    SequentialCompanyIdAllocator,
)





def make_discovery(name: str) -> RawDiscovery:
    return RawDiscovery(
        source=Source.FINELIB,
        business_name=name,
    )


@pytest.mark.asyncio
async def test_batch_processor_processes_multiple_discoveries():

    company_repository = InMemoryCompanyRepository()

    match_repository = InMemoryCompanyMatchRepository()

    resolution = EntityResolutionService(
        repository=match_repository,
        engine=EntityResolutionEngine(),
    )

    registry = DiscoveryCompanyRegistryService(
        repository=company_repository,
        resolution_service=resolution,
        factory=CompanyFactory(id_allocator=SequentialCompanyIdAllocator(),),
        merge_service=CompanyMergeService(),
    )

    processor = DiscoveryProcessor(
        registry_service=registry,
    )

    batch = DiscoveryBatchProcessor(
        processor=processor,
    )

    companies = await batch.process(
        [
            make_discovery("Drugstoc"),
            make_discovery("Helium Health"),
            make_discovery("Reliance Health"),
        ]
    )

    assert len(companies) == 3

    assert await company_repository.count() == 3
