from __future__ import annotations

from acios_discovery.domain.crawling.crawl_checkpoint import (
    CrawlCheckpoint,
)
from acios_discovery.domain.repositories.crawl_checkpoint_repository import (
    CrawlCheckpointRepository,
)


class InMemoryCrawlCheckpointRepository(
    CrawlCheckpointRepository,
):
    def __init__(self) -> None:
        self._items: dict[str, CrawlCheckpoint] = {}

    async def save(
        self,
        checkpoint: CrawlCheckpoint,
    ) -> None:
        self._items[checkpoint.session_id] = checkpoint

    async def get(
        self,
        session_id: str,
    ) -> CrawlCheckpoint | None:
        return self._items.get(session_id)

    async def delete(
        self,
        session_id: str,
    ) -> None:
        self._items.pop(session_id, None)
