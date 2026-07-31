from uuid import uuid4

from pydantic import BaseModel, Field

from .priority import CrawlPriority
from .status import CrawlStatus


class CrawlJob(BaseModel):
    """
    Represents one crawl task.
    """

    id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    source: str

    listing_url: str

    state: str

    city: str

    category_slug: str

    page: int = 1

    priority: CrawlPriority = CrawlPriority.NORMAL

    retries: int = 0

    max_retries: int = 3

    status: CrawlStatus = CrawlStatus.PENDING
