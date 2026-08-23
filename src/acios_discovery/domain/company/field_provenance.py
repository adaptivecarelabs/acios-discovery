from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class FieldProvenance:
    """
    Records where a single contributed value came from,
    and how confident the resolution was that it belongs
    to this company.
    """

    source: str

    detail_url: str | None

    confidence: float

    observed_at: datetime
