from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class RawDiscovery:
    """
    Represents an unverified company listing harvested from a source.
    """

    source: str
    business_name: str
    phone_number: str | None = None
    address: str | None = None
    description: str | None = None
    category: str | None = None
    city: str | None = None
    state: str | None = None
    discovered_at: datetime = datetime.now(UTC)

    def __post_init__(self) -> None:
        if not self.business_name.strip():
            raise ValueError("business_name cannot be empty")
