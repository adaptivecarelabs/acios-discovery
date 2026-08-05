from __future__ import annotations

from pydantic import BaseModel

from acios_discovery.domain.sources import Source


class DetailUrl(BaseModel):
    """
    Represents a single company detail page
    discovered from a listing page.
    """

    source: Source

    url: str

    state: str

    city: str

    category_slug: str
