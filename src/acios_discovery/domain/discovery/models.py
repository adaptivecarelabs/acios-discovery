from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from pydantic import Field


@dataclass(frozen=True, slots=True)
class RawDiscovery:
    source: str
    business_name: str

    detail_url: str | None = None

    phone_numbers: list[str] = Field(default_factory=list)
    address: str | None = None
    description: str | None = None

    category: str | None = None
    city: str | None = None
    state: str | None = None

    discovered_at: datetime = datetime.now(UTC)

    def __post_init__(self) -> None:
        if not self.business_name.strip():
            raise ValueError("business_name cannot be empty")
