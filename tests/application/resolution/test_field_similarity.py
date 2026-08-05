import pytest

from acios_discovery.application.resolution.field_similarity import (
    address_match,
    normalize_address,
    normalize_phone,
    normalize_text,
    phone_match,
    same_domain,
    similarity,
)

# ---------------------------------------------------------
# normalize_text
# ---------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Drugstoc Ltd", "DRUGSTOC LTD"),
        ("Health-Care", "HEALTH CARE"),
        ("ABC, Inc.", "ABC INC"),
        ("Multiple   Spaces", "MULTIPLE SPACES"),
        ("", ""),
        (None, ""),
    ],
)
def test_normalize_text(
    raw,
    expected,
):
    assert normalize_text(raw) == expected


# ---------------------------------------------------------
# similarity
# ---------------------------------------------------------


def test_similarity_identical():
    assert similarity(
        "Drugstoc",
        "Drugstoc",
    ) == 1.0


def test_similarity_case_insensitive():
    assert similarity(
        "drugstoc",
        "DRUGSTOC",
    ) == 1.0


def test_similarity_similar_names():
    score = similarity(
        "Drugstoc",
        "Drug Stock",
    )

    assert score > 0.75


def test_similarity_different():
    score = similarity(
        "Drugstoc",
        "Zenith Bank",
    )

    assert score < 0.40


# ---------------------------------------------------------
# phone normalization
# ---------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("+234 803 123 4567", "2348031234567"),
        ("0803-123-4567", "08031234567"),
        ("(0803) 123 4567", "08031234567"),
        ("", ""),
        (None, ""),
    ],
)
def test_normalize_phone(
    raw,
    expected,
):
    assert normalize_phone(raw) == expected


def test_phone_match_same():
    assert phone_match(
        "+2348031234567",
        "+234 803 123 4567",
    )


def test_phone_match_different():
    assert not phone_match(
        "08031234567",
        "08145555555",
    )


# ---------------------------------------------------------
# address normalization
# ---------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            "12 Broad Street, Lagos.",
            "12 BROAD STREET LAGOS",
        ),
        (
            "No. 15 Allen Ave",
            "NO 15 ALLEN AVE",
        ),
        (
            "",
            "",
        ),
        (
            None,
            "",
        ),
    ],
)
def test_normalize_address(
    raw,
    expected,
):
    assert normalize_address(raw) == expected


def test_address_match():
    assert address_match(
        "12 Broad Street Lagos",
        "12 Broad Street, Lagos",
    )


def test_address_not_match():
    assert not address_match(
        "12 Broad Street Lagos",
        "55 Allen Avenue Ikeja",
    )


# ---------------------------------------------------------
# domains
# ---------------------------------------------------------


def test_same_domain_true():
    assert same_domain(
        "info@drugstoc.com",
        "sales@drugstoc.com",
    )


def test_same_domain_false():
    assert not same_domain(
        "hello@drugstoc.com",
        "contact@zenithbank.com",
    )


def test_same_domain_handles_none():
    assert not same_domain(
        None,
        None,
    )
