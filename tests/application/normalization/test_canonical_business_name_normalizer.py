import pytest

from acios_discovery.application.normalization.canonical_business_name import (
    CanonicalBusinessNameNormalizer,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            "Drugstoc EHub Ltd",
            "DRUGSTOC EHUB",
        ),
        (
            "Drugstoc EHub Limited",
            "DRUGSTOC EHUB",
        ),
        (
            "Zenith Bank PLC",
            "ZENITH BANK",
        ),
        (
            "ABC & Sons Ltd",
            "ABC AND SONS",
        ),
        (
            "Example, Inc.",
            "EXAMPLE",
        ),
        (
            "Example Company",
            "EXAMPLE",
        ),
        (
            "Acme Corporation",
            "ACME",
        ),
        (
            "Health-Care Limited",
            "HEALTH CARE",
        ),
        (
            "  Example Ltd  ",
            "EXAMPLE",
        ),
        (
            "",
            "",
        ),
    ],
)
def test_canonical_normalization(
    raw: str,
    expected: str,
) -> None:

    normalizer = CanonicalBusinessNameNormalizer()

    assert (
        normalizer.normalize(raw)
        == expected
    )
