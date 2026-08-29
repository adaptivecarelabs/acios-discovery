from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.domain.cac import (
    CacEntityType,
    CacRegistrationStatus,
    CacSearchResult,
    CacVerificationResult,
    VerificationOutcome,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.infrastructure.persistence.repositories.cac_verification_repository import (
    SqlAlchemyCacVerificationRepository,
)
from acios_discovery.infrastructure.persistence.repositories.company_repository import (
    SqlAlchemyCompanyRepository,
)


def make_company(
    sequence: int = 1,
    name: str = "Drugstoc EHub Ltd",
) -> Company:
    return Company(
        id=CompanyId.from_sequence(sequence),
        canonical_name=name,
    )


def make_verified_result(
    company_id: str,
) -> CacVerificationResult:

    matched = CacSearchResult(
        approved_name="DRUGSTOC EHUB LIMITED",
        rc_number="RC123456",
        company_id=987654,
        entity_type=CacEntityType.COMPANY,
        registration_date=datetime(2020, 1, 1, tzinfo=UTC),
        nature_of_business="Pharmaceutical distribution",
        status=CacRegistrationStatus.ACTIVE,
    )

    return CacVerificationResult(
        company_id=company_id,
        searched_name="DRUGSTOC",
        outcome=VerificationOutcome.VERIFIED,
        matched_entity=matched,
        confidence=95.0,
    )


def make_not_found_result(
    company_id: str,
) -> CacVerificationResult:

    return CacVerificationResult(
        company_id=company_id,
        searched_name="UNKNOWN CO",
        outcome=VerificationOutcome.NOT_FOUND,
        matched_entity=None,
        confidence=0.0,
    )


def make_ambiguous_result(
    company_id: str,
) -> CacVerificationResult:

    return CacVerificationResult(
        company_id=company_id,
        searched_name="AMBIGUOUS CO",
        outcome=VerificationOutcome.AMBIGUOUS,
        matched_entity=None,
        confidence=40.0,
    )


async def _persist_company(
    db_session: AsyncSession,
    company: Company,
) -> None:

    company_repository = SqlAlchemyCompanyRepository(db_session)

    await company_repository.add(company)

    await db_session.commit()


async def test_add_and_get_latest_for_company(
    db_session: AsyncSession,
) -> None:

    company = make_company()

    await _persist_company(db_session, company)

    repository = SqlAlchemyCacVerificationRepository(db_session)

    result = make_verified_result(company.id.value)

    await repository.add(result)

    await db_session.commit()

    loaded = await repository.get_latest_for_company(
        company.id.value,
    )

    assert loaded is not None
    assert loaded.outcome == VerificationOutcome.VERIFIED
    assert loaded.matched_entity is not None
    assert loaded.matched_entity.rc_number == "RC123456"
    assert loaded.matched_entity.nature_of_business == (
        "Pharmaceutical distribution"
    )
    assert loaded.confidence == 95.0


async def test_get_latest_for_company_returns_none_when_unattempted(
    db_session: AsyncSession,
) -> None:

    company = make_company()

    await _persist_company(db_session, company)

    repository = SqlAlchemyCacVerificationRepository(db_session)

    loaded = await repository.get_latest_for_company(
        company.id.value,
    )

    assert loaded is None


async def test_get_latest_for_company_returns_most_recent_attempt(
    db_session: AsyncSession,
) -> None:

    company = make_company()

    await _persist_company(db_session, company)

    repository = SqlAlchemyCacVerificationRepository(db_session)

    await repository.add(
        make_ambiguous_result(company.id.value),
    )

    await db_session.commit()

    await repository.add(
        make_verified_result(company.id.value),
    )

    await db_session.commit()

    loaded = await repository.get_latest_for_company(
        company.id.value,
    )

    assert loaded is not None
    assert loaded.outcome == VerificationOutcome.VERIFIED


async def test_get_terminal_company_ids_includes_verified(
    db_session: AsyncSession,
) -> None:

    company = make_company(sequence=1)

    await _persist_company(db_session, company)

    repository = SqlAlchemyCacVerificationRepository(db_session)

    await repository.add(
        make_verified_result(company.id.value),
    )

    await db_session.commit()

    terminal_ids = await repository.get_terminal_company_ids()

    assert company.id.value in terminal_ids


async def test_get_terminal_company_ids_includes_not_found(
    db_session: AsyncSession,
) -> None:

    company = make_company(sequence=1)

    await _persist_company(db_session, company)

    repository = SqlAlchemyCacVerificationRepository(db_session)

    await repository.add(
        make_not_found_result(company.id.value),
    )

    await db_session.commit()

    terminal_ids = await repository.get_terminal_company_ids()

    assert company.id.value in terminal_ids


async def test_get_terminal_company_ids_excludes_ambiguous(
    db_session: AsyncSession,
) -> None:

    company = make_company(sequence=1)

    await _persist_company(db_session, company)

    repository = SqlAlchemyCacVerificationRepository(db_session)

    await repository.add(
        make_ambiguous_result(company.id.value),
    )

    await db_session.commit()

    terminal_ids = await repository.get_terminal_company_ids()

    assert company.id.value not in terminal_ids


async def test_get_terminal_company_ids_excludes_unattempted(
    db_session: AsyncSession,
) -> None:

    company = make_company(sequence=1)

    await _persist_company(db_session, company)

    repository = SqlAlchemyCacVerificationRepository(db_session)

    terminal_ids = await repository.get_terminal_company_ids()

    assert company.id.value not in terminal_ids
