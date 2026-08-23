from acios_discovery.application.company.company_factory import (
    CompanyFactory,
)
from acios_discovery.application.company.sequential_company_id_allocator import (
    SequentialCompanyIdAllocator,
)
from acios_discovery.domain.discovery.models import (
    RawDiscovery,
)
from acios_discovery.domain.sources import Source


def make_discovery() -> RawDiscovery:
    return RawDiscovery(
        source=Source.FINELIB,
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


def make_factory() -> CompanyFactory:
    return CompanyFactory(
        id_allocator=SequentialCompanyIdAllocator(),
    )


async def test_factory_creates_company():
    factory = make_factory()

    company = await factory.create(
        discovery=make_discovery(),
    )

    assert str(company.id) == "ACL-COM-00000001"

    assert company.canonical_name == "DRUGSTOC EHUB"

    assert "Drugstoc EHub Ltd" in company.aliases

    assert "08030000000" in company.phone_numbers

    assert "hello@drugstoc.com" in company.emails

    assert "https://drugstoc.com" in company.websites

    assert "12 Broad Street" in company.addresses

    assert "Lagos" in company.cities

    assert "Pharmacy" in company.categories

    assert Source.FINELIB in company.sources


async def test_factory_generates_new_ids():
    factory = make_factory()

    first = await factory.create(
        discovery=make_discovery(),
    )

    second = await factory.create(
        discovery=make_discovery(),
    )

    assert first.id != second.id


async def test_factory_keeps_original_name_as_alias():
    factory = make_factory()

    company = await factory.create(
        discovery=make_discovery(),
    )

    assert "Drugstoc EHub Ltd" in company.aliases


async def test_factory_canonicalizes_name():
    factory = make_factory()

    company = await factory.create(
        discovery=make_discovery(),
    )

    assert company.canonical_name == "DRUGSTOC EHUB"


async def test_factory_copies_description():

    factory = make_factory()

    company = await factory.create(
        discovery=make_discovery(),
    )

    assert company.description == (
        "A healthcare technology company."
    )


async def test_factory_records_provenance_at_founding_confidence():

    factory = make_factory()

    company = await factory.create(
        discovery=make_discovery(),
    )

    assert company.scalar_provenance["description"].confidence == 100.0
    assert company.scalar_provenance["description"].source == Source.FINELIB

    assert "08030000000" in company.set_provenance["phone_numbers"]

    assert (
        company.set_provenance["phone_numbers"]["08030000000"].confidence
        == 100.0
    )

    assert (
        company.set_provenance["phone_numbers"]["08030000000"].source
        == Source.FINELIB
    )
