from datetime import UTC, datetime

from pydantic import BaseModel, Field


class DiscoveryContext(BaseModel):
    """
    Metadata describing where and how
    a company was discovered.
    """

    source: str

    country: str = "Nigeria"

    state: str

    city: str

    industry: str | None = None

    sector: str | None = None

    category: str

    subcategory: str | None = None

    listing_url: str

    page_number: int = 1

    discovered_at: datetime = Field(
        default_factory=lambda: datetime.now(
            UTC
        )
    )
