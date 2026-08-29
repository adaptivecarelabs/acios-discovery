from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .cac_entity_type import CacEntityType
from .cac_registration_status import CacRegistrationStatus


@dataclass(frozen=True, slots=True)
class CacSearchResult:
    """
    One candidate returned by CAC's public search API for a
    given search term. A search typically returns several
    loosely-related candidates, not a single definitive match —
    see CacVerificationService for how a specific candidate is
    selected as the verified match (or none is, if nothing
    clears the confidence threshold).

    Several fields are genuinely nullable in CAC's real
    responses — rc_number and registration_date are frequently
    null for LLP/LP/IT entities and even some newly-registered
    COMPANY/BUSINESS_NAME entries, independent of entity type.
    A result whose approved_name is null carries no usable
    signal at all and should be filtered out at the parsing
    boundary rather than constructed here.
    """

    approved_name: str

    rc_number: str | None

    company_id: int

    entity_type: CacEntityType

    registration_date: datetime | None

    nature_of_business: str

    status: CacRegistrationStatus | None
