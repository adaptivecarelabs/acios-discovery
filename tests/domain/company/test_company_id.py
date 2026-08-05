import pytest

from acios_discovery.domain.company.company_id import (
    CompanyId,
)


def test_from_sequence():

    identifier = CompanyId.from_sequence(
        1,
    )

    assert str(
        identifier,
    ) == "COMP-00000001"


def test_large_sequence():

    identifier = CompanyId.from_sequence(
        152,
    )

    assert str(
        identifier,
    ) == "COMP-00000152"


def test_parse():

    identifier = CompanyId.parse(
        "COMP-00000045",
    )

    assert identifier.value == "COMP-00000045"


def test_invalid_parse():

    with pytest.raises(
        ValueError,
    ):
        CompanyId.parse(
            "ABC-0001",
        )


def test_invalid_sequence():

    with pytest.raises(
        ValueError,
    ):
        CompanyId.from_sequence(
            0,
        )
