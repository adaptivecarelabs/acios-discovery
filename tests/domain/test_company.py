from dataclasses import FrozenInstanceError

import pytest

from acios_discovery.domain.entities.company import Company


def test_company_creation() -> None:
    company = Company(
        business_name="Adaptive Care Labs Ltd",
        rc_number="RC123456",
        status="ACTIVE",
        phone_number="+2348031234567",
    )

    assert company.business_name == "Adaptive Care Labs Ltd"
    assert company.rc_number == "RC123456"
    assert company.status == "ACTIVE"


def test_business_name_required() -> None:
    with pytest.raises(ValueError):
        Company(
            business_name="",
            rc_number="RC123456",
            status="ACTIVE",
        )


def test_company_is_immutable() -> None:
    company = Company(
        business_name="Adaptive Care Labs Ltd",
        rc_number="RC123456",
        status="ACTIVE",
    )

    with pytest.raises(FrozenInstanceError):
        company.status = "INACTIVE"
