import pytest

from acios_discovery.application.resolution.entity_resolution_engine import (
    EntityResolutionEngine,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.domain.discovery.models import (
    RawDiscovery,
)
from acios_discovery.domain.sources import Source


def make_company(
    canonical_name: str,
    phone: str | None = None,
    website: str | None = None,
) -> Company:

    company = Company(
        id = CompanyId.from_sequence(1),
        canonical_name=canonical_name,
    )

    if phone:
        company.add_phone(phone)

    if website:
        company.add_website(website)

    return company



def make_discovery(
    name: str,
    phone: str | None = None,
    website: str | None = None,
) -> RawDiscovery:

    return RawDiscovery(
        source=Source.FINELIB,
        business_name=name,
        phone_numbers=[phone] if phone else [],
        website=website,
    )




@pytest.fixture
def engine() -> EntityResolutionEngine:
    return EntityResolutionEngine()


def test_identical_names_match(engine: EntityResolutionEngine):

    discovery = make_discovery("Drugstoc EHub Ltd")
    company = make_company("Drugstoc EHub Limited")

    score = engine.confidence(discovery, company)

    assert score == pytest.approx(60.0)


def test_different_names_do_not_match(engine: EntityResolutionEngine):

    discovery = make_discovery("Drugstoc")
    company = make_company("Zenith Bank")

    score = engine.confidence(discovery, company)

    assert score < 80


def test_same_phone_increases_confidence(engine: EntityResolutionEngine):

    discovery = make_discovery(
        "Drugstoc",
        phone="08030000000",
    )

    company = make_company(
        "Different Name",
        phone="08030000000",
    )

    score = engine.confidence(discovery, company)

    assert score > 0


def test_same_website_increases_confidence(engine: EntityResolutionEngine):

    discovery = make_discovery(
        "ABC",
        website="https://abc.com",
    )

    company = make_company(
        "XYZ",
        website="https://abc.com",
    )

    score = engine.confidence(discovery, company)

    assert score > 0


def test_phone_and_name_produce_higher_score(
    engine: EntityResolutionEngine,
):

    discovery = make_discovery(
        "Drugstoc",
        phone="08030000000",
    )

    company = make_company(
        "Drugstoc Ltd",
        phone="08030000000",
    )

    score = engine.confidence(discovery, company)

    assert score >= 80



def test_alias_matches(engine: EntityResolutionEngine):

    discovery = make_discovery(
        "Drugstoc EHub Ltd",
    )

    company = make_company(
        "DRUGSTOC",
    )

    company.add_alias(
        "Drugstoc EHub Ltd",
    )

    score = engine.confidence(
        discovery,
        company,
    )

    assert score == pytest.approx(60.0)



def test_exact_normalized_name_match_is_full_confidence(
    engine: EntityResolutionEngine,
):
    """
    Regression test for the Me Cure Healthcare production incident.

    An incoming discovery whose name normalizes to exactly the
    same canonical name as an existing company must score as a
    full-confidence match, even with zero corroborating phone,
    email, website, or address signals. Without this, an exact
    name match can score as low as NAME_WEIGHT (60), which falls
    below the STRONG_MATCH threshold (80) and causes the registry
    to attempt creating a duplicate company, colliding with the
    canonical_name unique constraint.
    """

    discovery = make_discovery("Me Cure Healthcare")

    company = make_company("ME CURE HEALTHCARE")

    score = engine.confidence(discovery, company)

    assert score == 100.0


def test_exact_normalized_name_match_wins_even_with_conflicting_signals(
    engine: EntityResolutionEngine,
):
    """
    An exact canonical name match should win even when the
    discovery's other fields point at DIFFERENT existing data
    (e.g. a different phone number or website domain on file) —
    this mirrors the real incident where the discovery's email/
    website domain (.com) differed from what was already stored
    for the company (.com.ng).
    """

    discovery = make_discovery(
        "Me Cure Healthcare",
        phone="08129910710",
        website="https://www.mecure.com",
    )

    company = make_company(
        "ME CURE HEALTHCARE",
        phone="08110095954",
        website="https://mecure.com.ng",
    )

    score = engine.confidence(discovery, company)

    assert score == 100.0


def test_fuzzy_name_without_corroboration_stays_below_strong_match(
    engine: EntityResolutionEngine,
):
    """
    Guardrail: the exact-match shortcut must NOT loosen fuzzy
    matching. A similar-but-not-identical name with no
    corroborating signals should still fall below the
    STRONG_MATCH threshold, exactly as before this fix.
    """

    discovery = make_discovery("Mee Cure Health Care")

    company = make_company("ME CURE HEALTHCARE")

    score = engine.confidence(discovery, company)

    assert score < 80.0

