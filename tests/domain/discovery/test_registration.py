from datetime import date

from acios_discovery.domain.discovery.registration import (
    BusinessRegistration,
)


def test_registration_defaults_to_none() -> None:
    registration = BusinessRegistration()

    assert registration.registration_number is None
    assert registration.entity_type is None
    assert registration.incorporation_date is None
    assert registration.status is None


def test_registration_accepts_cac_values() -> None:
    registration = BusinessRegistration(
        registration_number="RC123456",
        entity_type="COMPANY",
        incorporation_date=date(2020, 5, 12),
        status="ACTIVE",
    )

    assert registration.registration_number == "RC123456"
    assert registration.entity_type == "COMPANY"
    assert registration.incorporation_date == date(2020, 5, 12)
    assert registration.status == "ACTIVE"
