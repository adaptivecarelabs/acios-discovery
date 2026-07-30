import pytest
from pydantic import ValidationError

from acios_discovery.domain.discovery.identity import (
    BusinessIdentity,
)


def test_business_identity_can_be_created() -> None:
    identity = BusinessIdentity(
        business_name="Drugstoc EHub Ltd",
    )

    assert identity.business_name == "Drugstoc EHub Ltd"
    assert identity.normalized_name is None


def test_business_identity_accepts_normalized_name() -> None:
    identity = BusinessIdentity(
        business_name="Drugstoc EHub Ltd",
        normalized_name="Drugstoc EHub",
    )

    assert identity.business_name == "Drugstoc EHub Ltd"
    assert identity.normalized_name == "Drugstoc EHub"


def test_business_name_is_required() -> None:
    with pytest.raises(ValidationError):
        BusinessIdentity()
