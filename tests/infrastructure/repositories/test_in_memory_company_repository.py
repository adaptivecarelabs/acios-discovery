import pytest

from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.infrastructure.repositories.in_memory_company_repository import (
    InMemoryCompanyRepository,
)


@pytest.mark.asyncio
async def test_add_company():

    repository = InMemoryCompanyRepository()

    company = Company(
        id=CompanyId.from_sequence(1),
        canonical_name="DRUGSTOC",
    )

    await repository.add(company)

    assert await repository.count() == 1


@pytest.mark.asyncio
async def test_get_company():

    repository = InMemoryCompanyRepository()

    company = Company(
        id=CompanyId.from_sequence(1),
        canonical_name="DRUGSTOC",
    )

    await repository.add(company)

    loaded = await repository.get(company.id)

    assert loaded is company


@pytest.mark.asyncio
async def test_list_all():

    repository = InMemoryCompanyRepository()

    for i in range(3):

        await repository.add(
            Company(
                id=CompanyId.from_sequence(i + 1),
                canonical_name=f"COMPANY {i}",
            )
        )

    companies = await repository.list_all()

    assert len(companies) == 3


@pytest.mark.asyncio
async def test_update_company():

    repository = InMemoryCompanyRepository()

    company = Company(
        id=CompanyId.from_sequence(1),
        canonical_name="DRUGSTOC",
    )

    await repository.add(company)

    company.add_alias(
        "Drugstoc Ltd",
    )

    await repository.update(company)

    loaded = await repository.get(company.id)

    assert "Drugstoc Ltd" in loaded.aliases
