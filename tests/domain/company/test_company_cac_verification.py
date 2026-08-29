from datetime import UTC, datetime

from acios_discovery.domain.cac import (
    CacEntityType,
    CacRegistrationStatus,
    CacSearchResult,
    CacVerificationResult,
    VerificationOutcome,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_id import CompanyId


def make_verified_result(
    company_id: str = "1",
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


def test_apply_cac_verification_sets_fields_on_verified():

    company = Company(
        id=CompanyId.from_sequence(1),
        canonical_name="DRUGSTOC",
    )

    result = make_verified_result()

    company.apply_cac_verification(result)

    assert company.rc_number == "RC123456"
    assert company.entity_type == CacEntityType.COMPANY
    assert company.registration_date == datetime(
        2020, 1, 1, tzinfo=UTC,
    )
    assert company.registration_status == (
        CacRegistrationStatus.ACTIVE
    )
    assert company.nature_of_business == (
        "Pharmaceutical distribution"
    )


def test_apply_cac_verification_records_provenance():

    company = Company(
        id=CompanyId.from_sequence(1),
        canonical_name="DRUGSTOC",
    )

    company.apply_cac_verification(make_verified_result())

    for field_name in (
        "rc_number",
        "entity_type",
        "registration_date",
        "registration_status",
        "nature_of_business",
    ):
        provenance = company.scalar_provenance[field_name]
        assert provenance.source == "CAC"
        assert provenance.confidence == 95.0


def test_apply_cac_verification_ignores_not_found():

    company = Company(
        id=CompanyId.from_sequence(1),
        canonical_name="DRUGSTOC",
    )

    result = CacVerificationResult(
        company_id="1",
        searched_name="DRUGSTOC",
        outcome=VerificationOutcome.NOT_FOUND,
        matched_entity=None,
        confidence=0.0,
    )

    company.apply_cac_verification(result)

    assert company.rc_number is None
    assert company.entity_type is None
    assert company.scalar_provenance == {}


def test_apply_cac_verification_ignores_ambiguous():

    company = Company(
        id=CompanyId.from_sequence(1),
        canonical_name="DRUGSTOC",
    )

    result = CacVerificationResult(
        company_id="1",
        searched_name="DRUGSTOC",
        outcome=VerificationOutcome.AMBIGUOUS,
        matched_entity=None,
        confidence=40.0,
    )

    company.apply_cac_verification(result)

    assert company.rc_number is None
    assert company.scalar_provenance == {}


def test_apply_cac_verification_always_overwrites_on_fresh_verified():

    company = Company(
        id=CompanyId.from_sequence(1),
        canonical_name="DRUGSTOC",
    )

    first = make_verified_result()

    company.apply_cac_verification(first)

    #
    # A second, lower-confidence VERIFIED result should still
    # overwrite — CAC is authoritative, most-recent wins,
    # regardless of confidence comparison.
    #

    second_matched = CacSearchResult(
        approved_name="DRUGSTOC EHUB LIMITED",
        rc_number="RC999999",
        company_id=987654,
        entity_type=CacEntityType.COMPANY,
        registration_date=datetime(2021, 6, 1, tzinfo=UTC),
        nature_of_business="Updated business line",
        status=CacRegistrationStatus.INACTIVE,
    )

    second = CacVerificationResult(
        company_id="1",
        searched_name="DRUGSTOC",
        outcome=VerificationOutcome.VERIFIED,
        matched_entity=second_matched,
        confidence=91.0,
    )

    company.apply_cac_verification(second)

    assert company.rc_number == "RC999999"
    assert company.registration_status == (
        CacRegistrationStatus.INACTIVE
    )
    assert company.scalar_provenance["rc_number"].confidence == 91.0
