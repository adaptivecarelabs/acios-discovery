from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_id import (
    CompanyId,
)


def test_company_initializes():

    company = Company(
        id=CompanyId.from_sequence(
            1,
        ),
        canonical_name="DRUGSTOC",
    )

    assert company.id == CompanyId.from_sequence(1,)

    assert str(company.id) == "COMP-00000001"

    assert company.canonical_name == "DRUGSTOC"

    assert company.active is True


def test_add_alias():

    company = Company(
        id="1",
        canonical_name="ABC",
    )

    company.add_alias(
        "ABC LTD",
    )

    company.add_alias(
        "ABC LTD",
    )

    assert len(
        company.aliases,
    ) == 1


def test_add_phone():

    company = Company(
        id="1",
        canonical_name="ABC",
    )

    company.add_phone(
        "0803",
    )

    company.add_phone(
        "0803",
    )

    assert len(
        company.phone_numbers,
    ) == 1


def test_add_email():

    company = Company(
        id="1",
        canonical_name="ABC",
    )

    company.add_email(
        "hello@test.com",
    )

    company.add_email(
        "hello@test.com",
    )

    assert len(
        company.emails,
    ) == 1


def test_add_website():

    company = Company(
        id="1",
        canonical_name="ABC",
    )

    company.add_website(
        "https://abc.com",
    )

    company.add_website(
        "https://abc.com",
    )

    assert len(
        company.websites,
    ) == 1


def test_touch_updates_last_seen():

    company = Company(
        id="1",
        canonical_name="ABC",
    )

    previous = company.last_seen

    company.touch()

    assert company.last_seen >= previous
