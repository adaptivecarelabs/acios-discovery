import pytest

from acios_discovery.application.normalization.business_name import (
    BusinessNameNormalizer,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Drugstoc EHub Ltd", "Drugstoc EHub"),
        ("ABC Nigeria Limited", "ABC Nigeria"),
        ("Zenith Bank PLC", "Zenith Bank"),
        ("Dangote Cement Plc", "Dangote Cement"),
        ("Smith & Sons", "Smith"),
        ("Example Nig. Ltd", "Example"),
        ("Example Nigeria Limited", "Example Nigeria"),
        ("Company Ltd.", "Company"),
        ("Company Limited ", "Company"),
        ("Company", "Company"),
    ],
)
def test_normalize_business_name(
    raw: str,
    expected: str,
) -> None:
    normalizer = BusinessNameNormalizer()

    assert normalizer.normalize(raw) == expected
