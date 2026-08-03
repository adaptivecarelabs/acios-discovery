from __future__ import annotations

from pydantic import BaseModel

from acios_discovery.domain.sources import Source


class ListingUrl(BaseModel):
    """
    Represents a downloadable listing page.
    """

    source: Source

    url: str

    state: str

    city: str

    taxonomy_slug: str

    page: int
