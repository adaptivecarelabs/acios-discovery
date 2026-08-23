from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.domain.discovery.models import RawDiscovery
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.repositories.in_memory_company_match_repository import (
    InMemoryCompanyMatchRepository,
)
from acios_discovery.infrastructure.repositories.in_memory_company_repository import (
    InMemoryCompanyRepository,
)


def make_company(
    name: str,
    sequence: int,
) -> Company:

    company = Company(
        id=CompanyId.from_sequence(sequence),
        canonical_name=name.upper(),
    )

    company.cities.add("Yaba")
    company.states.add("Lagos")

    return company


def make_discovery(
    name: str,
) -> RawDiscovery:
    return RawDiscovery(
        source=Source.FINELIB,
        business_name=name,
        city="Yaba",
        state="Lagos",
    )


# ---------------------------------------------------------
# Empty repository
# ---------------------------------------------------------


async def test_empty_repository_returns_no_candidates():

    company_repository = InMemoryCompanyRepository()

    repository = InMemoryCompanyMatchRepository(
        company_repository,
    )

    candidates = await repository.candidates(
        make_discovery(
            "Drugstoc",
        ),
    )

    assert candidates == []


# ---------------------------------------------------------
# Single company
# ---------------------------------------------------------


async def test_repository_returns_added_company():

    company_repository = InMemoryCompanyRepository()

    repository = InMemoryCompanyMatchRepository(
        company_repository,
    )

    company = make_company(
        "Drugstoc",
        sequence=1,
    )

    await company_repository.add(
        company,
    )

    candidates = await repository.candidates(
        make_discovery(
            "Drugstoc Ltd",
        ),
    )

    assert len(candidates) == 1

    assert candidates[0].canonical_name == "DRUGSTOC"


# ---------------------------------------------------------
# Multiple companies, geography-scoped fallback
# ---------------------------------------------------------


async def test_repository_returns_geography_scoped_candidates():

    company_repository = InMemoryCompanyRepository()

    repository = InMemoryCompanyMatchRepository(
        company_repository,
    )

    await company_repository.add(
        make_company("Drugstoc", sequence=1),
    )

    await company_repository.add(
        make_company("Zenith Bank", sequence=2),
    )

    await company_repository.add(
        make_company("ABC Pharmacy", sequence=3),
    )

    candidates = await repository.candidates(
        make_discovery(
            "Drugstoc Limited",
        ),
    )

    # Only "Drugstoc" matches by name, but all three share the
    # same city/state as the incoming discovery, so all three
    # are returned as geography-scoped candidates for the fuzzy
    # scorer to evaluate.
    assert len(candidates) == 3


async def test_repository_excludes_companies_outside_geography_and_name():

    company_repository = InMemoryCompanyRepository()

    repository = InMemoryCompanyMatchRepository(
        company_repository,
    )

    await company_repository.add(
        make_company("Drugstoc", sequence=1),
    )

    unrelated = Company(
        id=CompanyId.from_sequence(2),
        canonical_name="ZENITH BANK",
    )

    unrelated.cities.add("Kano")
    unrelated.states.add("Kano")

    await company_repository.add(
        unrelated,
    )

    candidates = await repository.candidates(
        make_discovery(
            "Drugstoc Limited",
        ),
    )

    # "Zenith Bank" shares neither name nor geography with the
    # incoming discovery, so it must not appear as a candidate.
    assert len(candidates) == 1
    assert candidates[0].canonical_name == "DRUGSTOC"
