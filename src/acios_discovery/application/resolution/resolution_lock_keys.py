from __future__ import annotations

from acios_discovery.application.normalization.company_lookup import (
    normalize_company_email,
    normalize_company_name,
    normalize_company_phone,
    normalize_company_website,
)
from acios_discovery.domain.discovery.models import RawDiscovery


def build_resolution_lock_keys(
    discovery: RawDiscovery,
) -> list[str]:
    """
    Build the advisory-lock keys that must be held while resolving
    and registering this discovery, so two concurrent discoveries
    that could resolve to the same company can never race past
    each other.

    Keys are namespaced by field and returned sorted, so that any
    two callers with overlapping key sets always acquire them in
    the same order — required to prevent deadlocks between
    concurrent transactions each holding a subset of the other's
    keys.
    """

    keys: set[str] = set()

    normalized_name = normalize_company_name(
        discovery.business_name,
    )

    if normalized_name:
        keys.add(f"company_name:{normalized_name}")

    for phone in discovery.phone_numbers:

        normalized_phone = normalize_company_phone(phone)

        if normalized_phone:
            keys.add(f"company_phone:{normalized_phone}")

    if discovery.email:
        keys.add(
            f"company_email:{normalize_company_email(discovery.email)}",
        )

    if discovery.website:
        keys.add(
            "company_website:"
            f"{normalize_company_website(discovery.website)}",
        )

    return sorted(keys)
