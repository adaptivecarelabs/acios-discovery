from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from .cac_search_result import CacSearchResult
from .verification_outcome import VerificationOutcome


@dataclass(slots=True)
class CacVerificationResult:
    """
    The outcome of attempting to verify one discovered company
    against CAC's register.

    matched_entity is populated only when outcome is VERIFIED —
    a NOT_FOUND or AMBIGUOUS outcome means no single candidate
    cleared the confidence threshold, and matched_entity is None.
    """

    company_id: str

    searched_name: str

    outcome: VerificationOutcome

    matched_entity: CacSearchResult | None

    confidence: float

    verified_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )
