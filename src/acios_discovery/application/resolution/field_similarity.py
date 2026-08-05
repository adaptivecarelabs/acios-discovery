from __future__ import annotations

import re
from difflib import SequenceMatcher
from urllib.parse import urlparse


def normalize_text(value: str | None) -> str:
    """
    Produces a canonical comparison string.

    Used only for similarity calculations.
    """

    if not value:
        return ""

    value = value.upper()

    value = re.sub(
        r"[^A-Z0-9 ]+",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def similarity(
    left: str | None,
    right: str | None,
) -> float:
    """
    Returns a value between 0 and 1.
    """

    left = normalize_text(left)
    right = normalize_text(right)

    if not left or not right:
        return 0.0

    return SequenceMatcher(
        None,
        left,
        right,
    ).ratio()


def same_domain(
    left: str | None,
    right: str | None,
) -> bool:
    """
    Compares website or email domains.
    """

    if not left or not right:
        return False

    def extract(value: str) -> str:

        value = value.strip().lower()

        #
        # Email
        #

        if "@" in value:
            return value.split("@", 1)[1]

        #
        # Website
        #

        parsed = urlparse(value)

        domain = parsed.netloc or parsed.path

        domain = domain.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    return extract(left) == extract(right)


def normalize_phone(
    value: str | None,
) -> str:
    if not value:
        return ""

    return re.sub(
        r"\D",
        "",
        value,
    )


def phone_match(
    left: str | None,
    right: str | None,
) -> bool:
    """
    Exact phone comparison after removing formatting.
    """

    if not left or not right:
        return False

    return normalize_phone(left) == normalize_phone(right)


def normalize_address(
    value: str | None,
) -> str:
    return normalize_text(value)


def address_match(
    left: str | None,
    right: str | None,
) -> bool:
    """
    Simple normalized address comparison.
    """

    if not left or not right:
        return False

    return normalize_address(left) == normalize_address(right)
