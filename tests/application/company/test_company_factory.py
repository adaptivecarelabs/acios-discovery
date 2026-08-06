from acios_discovery.application.company.company_factory import (
    CompanyFactory,
)
from acios_discovery.domain.discovery.models import (
    RawDiscovery,
)
from acios_discovery.domain.sources import Source


def make_discovery() -> RawDiscovery:

    return RawDiscovery(
        source=Source.FINELIB,
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


def test_factory_creates_company():

    factory = CompanyFactory()

    company = factory.create(
        sequence=1,
        discovery=make_discovery(),
    )

    assert str(company.id) == "COMP-00000001"

    assert company.canonical_name == "DRUGSTOC EHUB"

    assert "Drugstoc EHub Ltd" in company.aliases

    assert "08030000000" in company.phone_numbers

    assert "hello@drugstoc.com" in company.emails

    assert "https://drugstoc.com" in company.websites

    assert "12 Broad Street" in company.addresses

    assert "Lagos" in company.cities

    assert "Pharmacy" in company.categories

    assert Source.FINELIB in company.sources


def test_factory_generates_new_ids():

    factory = CompanyFactory()

    first = factory.create(
        1,
        make_discovery(),
    )

    second = factory.create(
        2,
        make_discovery(),
    )

    assert first.id != second.id


def test_factory_keeps_original_name_as_alias():

    factory = CompanyFactory()

    company = factory.create(
        10,
        make_discovery(),
    )

    assert "Drugstoc EHub Ltd" in company.aliases


def test_factory_canonicalizes_name():

    factory = CompanyFactory()

    company = factory.create(
        1,
        make_discovery(),
    )

    assert company.canonical_name == "DRUGSTOC EHUB"
