from __future__ import annotations

from pydantic import BaseModel


class CrawlPlan(BaseModel):
    """
    Represents one listing page that should be crawled.
    """

    state: str

    city: str

    category_slug: str

    page: int = 1
