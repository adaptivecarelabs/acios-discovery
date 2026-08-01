from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class RawDiscovery:
    source: str

    business_name: str

    detail_url: str | None = None

    address: str | None = None

    description: str | None = None

    phone_numbers: list[str] = field(default_factory=list)

    #
    # Detail-page enrichment
    #

    email: str | None = None

    website: str | None = None

    social_links: dict[str, str] = field(default_factory=dict)

    year_founded: int | None = None

    employee_count: str | None = None

    business_locations: int | None = None

    product_types: list[str] = field(default_factory=list)

    payment_methods: list[str] = field(default_factory=list)

    #
    # Crawl metadata
    #

    category: str | None = None

    city: str | None = None

    state: str | None = None

    discovered_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    def __post_init__(self) -> None:

        if not self.business_name.strip():
            raise ValueError(
                "business_name cannot be empty"
            )
