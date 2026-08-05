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

    company = service.merge(
        make_company(),
        make_discovery(),
    )

    assert "Drugstoc Ltd" in company.aliases

    assert "Drugstoc EHub Ltd" in company.aliases


def test_merge_phone():

    service = CompanyMergeService()

    company = service.merge(
        make_company(),
        make_discovery(),
    )

    assert "08030000000" in company.phone_numbers


def test_merge_email():

    service = CompanyMergeService()

    company = service.merge(
        make_company(),
        make_discovery(),
    )

    assert "hello@drugstoc.com" in company.emails


def test_merge_website():

    service = CompanyMergeService()

    company = service.merge(
        make_company(),
        make_discovery(),
    )

    assert "https://drugstoc.com" in company.websites


def test_merge_source():

    service = CompanyMergeService()

    company = service.merge(
        make_company(),
        make_discovery(),
    )

    assert "Google" in company.sources


def test_merge_category():

    service = CompanyMergeService()

    company = service.merge(
        make_company(),
        make_discovery(),
    )

    assert "Pharmacy" in company.categories
