from acios_discovery.domain.discovery.models import (
    RawDiscovery,
)
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.repositories.in_memory_company_match_repository import (
    InMemoryCompanyMatchRepository,
)


def make_company(
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

    repository = InMemoryCompanyMatchRepository()

    candidates = await repository.candidates(
        make_company(
            "Drugstoc",
        ),
    )

    assert candidates == []


# ---------------------------------------------------------
# Single company
# ---------------------------------------------------------


async def test_repository_returns_added_company():

    repository = InMemoryCompanyMatchRepository()

    company = make_company(
        "Drugstoc",
    )

    await repository.add(
        company,
    )

    candidates = await repository.candidates(
        make_company(
            "Drugstoc Ltd",
        ),
    )

    assert len(
        candidates,
    ) == 1

    assert (
        candidates[0].business_name
        == "Drugstoc"
    )


# ---------------------------------------------------------
# Multiple companies
# ---------------------------------------------------------


async def test_repository_returns_all_candidates():

    repository = InMemoryCompanyMatchRepository()

    await repository.add(
        make_company(
            "Drugstoc",
        ),
    )

    await repository.add(
        make_company(
            "Zenith Bank",
        ),
    )

    await repository.add(
        make_company(
            "ABC Pharmacy",
        ),
    )

    candidates = await repository.candidates(
        make_company(
            "Drugstoc Limited",
        ),
    )

    assert len(
        candidates,
    ) == 3
