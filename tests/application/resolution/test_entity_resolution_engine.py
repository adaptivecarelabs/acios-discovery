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
