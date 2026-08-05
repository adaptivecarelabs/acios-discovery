import pytest

from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.infrastructure.repositories.in_memory_company_repository import (
    InMemoryCompanyRepository,
)


def make_company(
    name: str,
) -> Company:

    return Company(
        id=CompanyId.from_sequence(1),
        canonical_name=name,
    )


@pytest.mark.asyncio
async def test_find_by_name():

    repo = InMemoryCompanyRepository()

    company = make_company(
        "Drugstoc",
    )

    await repo.add(company)

    result = await repo.find_by_name(
        "Drugstoc",
    )

    assert result is company


@pytest.mark.asyncio
async def test_find_by_alias():

    repo = InMemoryCompanyRepository()

    company = make_company(
        "Drugstoc",
    )

    company.add_alias(
        "Drugstoc EHub Ltd",
    )

    await repo.add(company)

    result = await repo.find_by_name(
        "Drugstoc EHub Ltd",
    )

    assert result is company


@pytest.mark.asyncio
async def test_find_by_phone():

    repo = InMemoryCompanyRepository()

    company = make_company(
        "Drugstoc",
    )

    company.add_phone(
        "08030000000",
    )

    await repo.add(company)

    result = await repo.find_by_phone(
        "0803-000-0000",
    )

    assert result is company


@pytest.mark.asyncio
async def test_find_by_email():

    repo = InMemoryCompanyRepository()

    company = make_company(
        "Drugstoc",
    )

    company.add_email(
        "info@drugstoc.com",
    )

    await repo.add(company)

    result = await repo.find_by_email(
        "INFO@DRUGSTOC.COM",
    )

    assert result is company


@pytest.mark.asyncio
async def test_find_by_website():

    repo = InMemoryCompanyRepository()

    company = make_company(
        "Drugstoc",
    )

    company.add_website(
        "https://drugstoc.com",
    )

    await repo.add(company)

    result = await repo.find_by_website(
        "https://www.drugstoc.com",
    )

    assert result is company
