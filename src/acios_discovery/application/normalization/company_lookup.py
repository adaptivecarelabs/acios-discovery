from __future__ import annotations

import re
from urllib.parse import urlparse

from acios_discovery.application.normalization.canonical_business_name import (
    CanonicalBusinessNameNormalizer,
)
from acios_discovery.application.resolution.field_similarity import (
    normalize_phone,
)

_name_normalizer = CanonicalBusinessNameNormalizer()


def normalize_company_name(value: str) -> str:
    """
    Normalize a company name for exact lookup.

    This uses the same canonical-name normalization
    used by entity resolution.
    """

    return _name_normalizer.normalize(value)


def normalize_company_alias(value: str) -> str:
    """
    Normalize a company alias for exact lookup.
    """

    return _name_normalizer.normalize(value)


def normalize_company_phone(value: str) -> str:
    """
    Normalize a company phone number for lookup.
    """

    return normalize_phone(value)


def normalize_company_email(value: str) -> str:
    """
    Normalize an email address for lookup.
    """

    return value.strip().lower()


def normalize_company_website(value: str) -> str:
    """
    Normalize a website into its hostname.

    Examples:

        https://drugstoc.com
        https://www.drugstoc.com/
        drugstoc.com

    all become:

        drugstoc.com
    """

    value = value.strip().lower()

    if not value:
        return ""

    if "://" not in value:
        value = f"https://{value}"

    parsed = urlparse(value)

    hostname = parsed.hostname or ""

    hostname = hostname.lower()

    hostname = hostname.removeprefix("www.")

    return hostname.rstrip(".")


def normalize_lookup_text(value: str) -> str:
    """
    Generic whitespace normalization for values
    that do not require field-specific processing.
    """

    return re.sub(
        r"\s+",
        " ",
        value.strip(),
    )
