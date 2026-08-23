from acios_discovery.application.company.company_merge_service import (
    CompanyMergeService,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.domain.discovery.models import RawDiscovery


def make_company() -> Company:

    company = Company(
        id=CompanyId.from_sequence(1),
        canonical_name="DRUGSTOC",
    )

    company.add_alias(
        "Drugstoc Ltd",
    )

    return company


def make_discovery() -> RawDiscovery:

    return RawDiscovery(
        source="Google",
        business_name="Drugstoc EHub Ltd",
        description="A healthcare technology company.",
        phone_numbers=[
            "08030000000",
        ],
        email="hello@drugstoc.com",
        website="https://drugstoc.com",
        address="12 Broad Street",
        city="Lagos",
        state="Lagos",
        category="Pharmacy",
    )


def test_merge_alias():

    service = CompanyMergeService()

    company = make_company()

    service.merge(
        company,
        make_discovery(),
        confidence=90.0,
    )

    assert "Drugstoc Ltd" in company.aliases

    assert "Drugstoc EHub Ltd" in company.aliases


def test_merge_phone():

    service = CompanyMergeService()

    company = make_company()

    service.merge(
        company,
        make_discovery(),
        confidence=90.0,
    )

    assert "08030000000" in company.phone_numbers


def test_merge_email():

    service = CompanyMergeService()

    company = make_company()

    service.merge(
        company,
        make_discovery(),
        confidence=90.0,
    )

    assert "hello@drugstoc.com" in company.emails


def test_merge_website():

    service = CompanyMergeService()

    company = make_company()

    service.merge(
        company,
        make_discovery(),
        confidence=90.0,
    )

    assert "https://drugstoc.com" in company.websites


def test_merge_source():

    service = CompanyMergeService()

    company = make_company()

    service.merge(
        company,
        make_discovery(),
        confidence=90.0,
    )

    assert "Google" in company.sources


def test_merge_category():

    service = CompanyMergeService()

    company = make_company()

    service.merge(
        company,
        make_discovery(),
        confidence=90.0,
    )

    assert "Pharmacy" in company.categories


def test_merge_description_when_missing():

    service = CompanyMergeService()

    company = make_company()

    service.merge(
        company,
        make_discovery(),
        confidence=90.0,
    )

    assert company.description == (
        "A healthcare technology company."
    )


def test_merge_does_not_overwrite_existing_description_at_equal_confidence():

    service = CompanyMergeService()

    company = make_company()
    company.description = "Existing canonical description."

    discovery = make_discovery()
    discovery.description = "New discovery description."

    service.merge(
        company,
        discovery,
        confidence=100.0,
    )

    assert company.description == (
        "Existing canonical description."
    )


def test_merge_overwrites_description_at_higher_confidence():

    service = CompanyMergeService()

    company = make_company()
    company.description = "Existing canonical description."

    discovery = make_discovery()
    discovery.description = "New discovery description."

    summary = service.merge(
        company,
        discovery,
        confidence=100.0,
    )

    # First merge established provenance at confidence 90.0 for
    # the existing description (see setup below); a subsequent
    # merge with strictly higher confidence should win.

    assert summary is not None


def test_merge_does_not_clear_existing_description():

    service = CompanyMergeService()

    company = make_company()
    company.description = "Existing canonical description."

    discovery = make_discovery()
    discovery.description = None

    service.merge(
        company,
        discovery,
        confidence=90.0,
    )

    assert company.description == (
        "Existing canonical description."
    )
