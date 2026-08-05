import pytest

from acios_discovery.application.resolution.entity_resolution_engine import (
    EntityResolutionEngine,
)
from acios_discovery.application.resolution.entity_resolution_service import (
    EntityResolutionService,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.domain.discovery.models import RawDiscovery
from acios_discovery.infrastructure.repositories.in_memory_company_repository import (
    InMemoryCompanyRepository,
)


def make_company(
    canonical_name: str,
    sequence: int = 1,
    phone: str | None = None,
    website: str | None = None,
) -> Company:

    company = Company(
        id=CompanyId.from_sequence(sequence),
        canonical_name=canonical_name,
    )

    if phone:
        company.add_phone(phone)

    if website:
        company.add_website(website)

    return company


@pytest.mark.asyncio
async def test_returns_no_match_when_repository_is_empty():

    repository = InMemoryCompanyRepository()

    service = EntityResolutionService(
        repository=repository,
        engine=EntityResolutionEngine(),
    )

    discovery = RawDiscovery(
        source="Finelib",
        business_name="Drugstoc EHub Ltd",
    )

    result = await service.resolve(
        discovery,
    )

    assert result.company is None
    assert result.duplicate is False
    assert result.confidence == 0.0


@pytest.mark.asyncio
async def test_detects_duplicate_by_name():

    repository = InMemoryCompanyRepository()

    existing = make_company(
        "Drugstoc EHub Ltd",
    )

    await repository.add(
        existing,
    )

    service = EntityResolutionService(
        repository=repository,
        engine=EntityResolutionEngine(),
    )

    incoming = RawDiscovery(
        source="Finelib",
        business_name="Drugstoc EHub Limited",
    )

    result = await service.resolve(
        incoming,
    )

    assert result.company is existing
    assert result.duplicate is True
    assert result.confidence >= 80.0


@pytest.mark.asyncio
async def test_returns_best_candidate():

    repository = InMemoryCompanyRepository()

    company1 = make_company(
        "ABC Logistics",
        sequence=1,
    )

    company2 = make_company(
        "Drugstoc EHub Ltd",
        sequence=2,
    )

    await repository.add(company1)
    await repository.add(company2)

    service = EntityResolutionService(
        repository=repository,
        engine=EntityResolutionEngine(),
    )

    incoming = RawDiscovery(
        source="Finelib",
        business_name="Drugstoc EHub Limited",
    )

    result = await service.resolve(
        incoming,
    )

    assert result.company is company2
    assert result.confidence > 0


@pytest.mark.asyncio
async def test_non_duplicate_when_similarity_is_low():

    repository = InMemoryCompanyRepository()

    await repository.add(
        make_company(
            "Zenith Bank",
        )
    )

    service = EntityResolutionService(
        repository=repository,
        engine=EntityResolutionEngine(),
    )

    incoming = RawDiscovery(
        source="Finelib",
        business_name="Drugstoc",
    )

    result = await service.resolve(
        incoming,
    )

    assert result.duplicate is False


@pytest.mark.asyncio
async def test_repository_candidates_are_used():

    repository = InMemoryCompanyRepository()

    for i in range(5):

        await repository.add(
            make_company(
                f"Company {i}",
                sequence=i + 1,
            )
        )

    service = EntityResolutionService(
        repository=repository,
        engine=EntityResolutionEngine(),
    )

    result = await service.resolve(
        RawDiscovery(
            source="Finelib",
            business_name="Company 3",
        )
    )

    assert result.company is not None
