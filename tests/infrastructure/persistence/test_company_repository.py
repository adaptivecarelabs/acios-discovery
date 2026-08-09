from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.infrastructure.persistence.repositories.company_repository import (
    SqlAlchemyCompanyRepository,
)


def make_company(
    sequence: int = 1,
    name: str = "Drugstoc EHub Ltd",
) -> Company:
    return Company(
        id=CompanyId.from_sequence(
            sequence,
        ),
        canonical_name=name,
    )


async def test_add_and_get_company(
    db_session: AsyncSession,
) -> None:
    repository = SqlAlchemyCompanyRepository(
        db_session,
    )

    company = make_company()

    await repository.add(
        company,
    )

    await db_session.commit()

    loaded = await repository.get(
        company.id,
    )

    assert loaded is not None
    assert loaded.id == company.id
    assert loaded.canonical_name == (
        "Drugstoc EHub Ltd"
    )


async def test_list_all_companies(
    db_session: AsyncSession,
) -> None:
    repository = SqlAlchemyCompanyRepository(
        db_session,
    )

    await repository.add(
        make_company(
            sequence=1,
            name="Company One",
        ),
    )

    await repository.add(
        make_company(
            sequence=2,
            name="Company Two",
        ),
    )

    await db_session.commit()

    companies = await repository.list_all()

    assert len(companies) == 2


async def test_count_companies(
    db_session: AsyncSession,
) -> None:
    repository = SqlAlchemyCompanyRepository(
        db_session,
    )

    await repository.add(
        make_company(
            sequence=1,
        ),
    )

    await repository.add(
        make_company(
            sequence=2,
            name="Another Company",
        ),
    )

    await db_session.commit()

    assert await repository.count() == 2


async def test_update_company(
    db_session: AsyncSession,
) -> None:
    repository = SqlAlchemyCompanyRepository(
        db_session,
    )

    company = make_company()

    await repository.add(
        company,
    )

    await db_session.commit()

    company.canonical_name = (
        "Drugstoc EHub Limited"
    )

    company.add_phone(
        "08030000000",
    )

    company.add_email(
        "contact@drugstoc.com",
    )

    company.add_website(
        "https://drugstoc.com",
    )

    await repository.update(
        company,
    )

    await db_session.commit()

    loaded = await repository.get(
        company.id,
    )

    assert loaded is not None

    assert loaded.canonical_name == (
        "Drugstoc EHub Limited"
    )

    assert "08030000000" in (
        loaded.phone_numbers
    )

    assert "contact@drugstoc.com" in (
        loaded.emails
    )

    assert "https://drugstoc.com" in (
        loaded.websites
    )


async def test_company_aliases_are_persisted_and_reloaded(
    db_session: AsyncSession,
) -> None:
    repository = SqlAlchemyCompanyRepository(
        db_session,
    )

    company = make_company()

    company.add_alias(
        "Drugstoc",
    )

    company.add_alias(
        "Drugstoc EHub",
    )

    await repository.add(
        company,
    )

    await db_session.commit()

    loaded = await repository.get(
        company.id,
    )

    assert loaded is not None

    assert loaded.aliases == {
        "Drugstoc",
        "Drugstoc EHub",
    }


async def test_find_by_canonical_name(
    db_session: AsyncSession,
) -> None:
    repository = SqlAlchemyCompanyRepository(
        db_session,
    )

    company = make_company()

    await repository.add(
        company,
    )

    await db_session.commit()

    loaded = await repository.find_by_name(
        "Drugstoc EHub Ltd",
    )

    assert loaded is not None
    assert loaded.id == company.id



async def test_find_by_email(
    db_session: AsyncSession,
) -> None:
    repository = SqlAlchemyCompanyRepository(
        db_session,
    )

    company = make_company()

    company.add_email(
        "contact@drugstoc.com",
    )

    await repository.add(company)

    await db_session.commit()

    loaded = await repository.find_by_email(
        "contact@drugstoc.com",
    )

    assert loaded is not None
    assert loaded.id == company.id


async def test_find_by_website(
    db_session: AsyncSession,
) -> None:
    repository = SqlAlchemyCompanyRepository(
        db_session,
    )

    company = make_company()

    company.add_website(
        "https://drugstoc.com",
    )

    await repository.add(company)

    await db_session.commit()

    loaded = await repository.find_by_website(
        "https://drugstoc.com",
    )

    assert loaded is not None
    assert loaded.id == company.id


async def test_find_by_canonical_name_is_normalized(
    db_session: AsyncSession,
) -> None:
    repository = SqlAlchemyCompanyRepository(
        db_session,
    )

    company = make_company(
        name="Drugstoc EHub Ltd",
    )

    await repository.add(company)

    await db_session.commit()

    loaded = await repository.find_by_name(
        "drugstoc ehub limited",
    )

    assert loaded is not None
    assert loaded.id == company.id


async def test_find_by_alias(
    db_session: AsyncSession,
) -> None:
    repository = SqlAlchemyCompanyRepository(
        db_session,
    )

    company = make_company()

    company.add_alias(
        "Drugstoc",
    )

    await repository.add(company)

    await db_session.commit()

    loaded = await repository.find_by_alias(
        "drugstoc",
    )

    assert loaded is not None
    assert loaded.id == company.id



async def test_find_by_phone(
    db_session: AsyncSession,
) -> None:
    repository = SqlAlchemyCompanyRepository(
        db_session,
    )

    company = make_company()

    company.add_phone(
        "08030000000",
    )

    await repository.add(company)

    await db_session.commit()

    loaded = await repository.find_by_phone(
        "08030000000",
    )

    assert loaded is not None
    assert loaded.id == company.id


async def test_find_by_email_is_case_insensitive(
    db_session: AsyncSession,
) -> None:
    repository = SqlAlchemyCompanyRepository(
        db_session,
    )

    company = make_company()

    company.add_email(
        "contact@drugstoc.com",
    )

    await repository.add(company)

    await db_session.commit()

    loaded = await repository.find_by_email(
        "CONTACT@DRUGSTOC.COM",
    )

    assert loaded is not None
    assert loaded.id == company.id


async def test_find_by_website_is_normalized(
    db_session: AsyncSession,
) -> None:
    repository = SqlAlchemyCompanyRepository(
        db_session,
    )

    company = make_company()

    company.add_website(
        "https://drugstoc.com",
    )

    await repository.add(company)

    await db_session.commit()

    loaded = await repository.find_by_website(
        "https://www.drugstoc.com/",
    )

    assert loaded is not None
    assert loaded.id == company.id
