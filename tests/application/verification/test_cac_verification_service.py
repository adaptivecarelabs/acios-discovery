import pytest

from acios_discovery.application.verification.cac_verification_service import (
    CacVerificationService,
)
from acios_discovery.domain.cac import (
    CacEntityType,
    CacRegistrationStatus,
    CacSearchResult,
    VerificationOutcome,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_id import CompanyId
from tests.fakes.fake_cac_search_client import FakeCacSearchClient


def make_company(
    name: str = "Drugstoc EHub Ltd",
) -> Company:
    return Company(
        id=CompanyId.from_sequence(1),
        canonical_name=name,
    )


def make_candidate(
    approved_name: str,
    status: CacRegistrationStatus | None = CacRegistrationStatus.ACTIVE,
) -> CacSearchResult:
    return CacSearchResult(
        approved_name=approved_name,
        rc_number="RC123456",
        company_id=1,
        entity_type=CacEntityType.COMPANY,
        registration_date=None,
        nature_of_business="Pharmaceutical distribution",
        status=status,
    )


@pytest.mark.asyncio
async def test_verify_returns_not_found_when_no_candidates():

    search_client = FakeCacSearchClient(
        responses={},
    )

    service = CacVerificationService(
        search_client=search_client,
    )

    result = await service.verify(make_company())

    assert result.outcome == VerificationOutcome.NOT_FOUND
    assert result.matched_entity is None
    assert result.confidence == 0.0


@pytest.mark.asyncio
async def test_verify_returns_verified_on_strong_match():

    search_client = FakeCacSearchClient(
        responses={
            "Drugstoc EHub Ltd": [
                make_candidate("DRUGSTOC EHUB LIMITED"),
            ],
        },
    )

    service = CacVerificationService(
        search_client=search_client,
    )

    result = await service.verify(make_company())

    assert result.outcome == VerificationOutcome.VERIFIED
    assert result.matched_entity is not None
    assert result.matched_entity.approved_name == (
        "DRUGSTOC EHUB LIMITED"
    )
    assert result.confidence == pytest.approx(100.0)


@pytest.mark.asyncio
async def test_verify_treats_ltd_and_limited_as_equivalent():
    """
    "Ltd" (as commonly used in discovered directory listings) and
    "Limited" (as CAC's register always spells it) must be
    treated as the same word, not penalized as a mismatch.
    """

    search_client = FakeCacSearchClient(
        responses={
            "Drugstoc EHub Ltd": [
                make_candidate("DRUGSTOC EHUB LIMITED"),
            ],
        },
    )

    service = CacVerificationService(
        search_client=search_client,
    )

    result = await service.verify(make_company("Drugstoc EHub Ltd"))

    assert result.outcome == VerificationOutcome.VERIFIED


@pytest.mark.asyncio
async def test_verify_returns_ambiguous_below_threshold():

    search_client = FakeCacSearchClient(
        responses={
            "Drugstoc EHub Ltd": [
                make_candidate("TOTALLY UNRELATED VENTURES"),
            ],
        },
    )

    service = CacVerificationService(
        search_client=search_client,
    )

    result = await service.verify(make_company())

    assert result.outcome == VerificationOutcome.AMBIGUOUS
    assert result.matched_entity is None


@pytest.mark.asyncio
async def test_verify_does_not_favor_partial_substring_match():
    """
    Regression test: a candidate name that is a near-exact
    prefix of the searched name plus extra trailing words (e.g.
    "DRUGSTOC EHUB LTD PARTIAL") must NOT outrank the true,
    fuller match ("DRUGSTOC EHUB LIMITED"). An earlier version of
    this service used WRatio, whose internal partial-ratio logic
    scored the unrelated "PARTIAL" candidate at 95.00 -- higher
    than the correct match at 89.47 -- which would have produced
    a false positive in production. token_sort_ratio does not
    have this substring bias.
    """

    search_client = FakeCacSearchClient(
        responses={
            "Drugstoc EHub Ltd": [
                make_candidate("DRUGSTOC EHUB LTD PARTIAL"),
                make_candidate("DRUGSTOC EHUB LIMITED"),
            ],
        },
    )

    service = CacVerificationService(
        search_client=search_client,
    )

    result = await service.verify(make_company())

    assert result.outcome == VerificationOutcome.VERIFIED
    assert result.matched_entity.approved_name == (
        "DRUGSTOC EHUB LIMITED"
    )


@pytest.mark.asyncio
async def test_verify_does_not_penalize_inactive_status():
    """
    An INACTIVE candidate with a passing name-similarity score
    is treated identically to an ACTIVE one — status is never a
    scoring factor.
    """

    search_client = FakeCacSearchClient(
        responses={
            "Drugstoc EHub Ltd": [
                make_candidate(
                    "DRUGSTOC EHUB LIMITED",
                    status=CacRegistrationStatus.INACTIVE,
                ),
            ],
        },
    )

    service = CacVerificationService(
        search_client=search_client,
    )

    result = await service.verify(make_company())

    assert result.outcome == VerificationOutcome.VERIFIED
    assert result.matched_entity.status == (
        CacRegistrationStatus.INACTIVE
    )


@pytest.mark.asyncio
async def test_verify_searches_using_canonical_name():

    search_client = FakeCacSearchClient(
        responses={
            "Drugstoc EHub Ltd": [
                make_candidate("DRUGSTOC EHUB LIMITED"),
            ],
        },
    )

    service = CacVerificationService(
        search_client=search_client,
    )

    await service.verify(make_company())

    assert search_client.requests == ["Drugstoc EHub Ltd"]


@pytest.mark.asyncio
async def test_verify_respects_custom_confidence_threshold():

    search_client = FakeCacSearchClient(
        responses={
            "Drugstoc EHub Ltd": [
                make_candidate("DRUGSTOC EHUB SOMEWHAT SIMILAR CO"),
            ],
        },
    )

    #
    # A very low threshold should accept a weaker match (measured
    # at ~66.67 under token_sort_ratio) that the default threshold
    # would reject as AMBIGUOUS.
    #

    service = CacVerificationService(
        search_client=search_client,
        confidence_threshold=1.0,
    )

    result = await service.verify(make_company())

    assert result.outcome == VerificationOutcome.VERIFIED
