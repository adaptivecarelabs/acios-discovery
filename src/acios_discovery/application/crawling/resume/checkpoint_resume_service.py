from __future__ import annotations

from acios_discovery.domain.crawling.crawl_checkpoint import (
    CrawlCheckpoint,
)
from acios_discovery.domain.crawling.crawl_checkpoint_repository import (
    CrawlCheckpointRepository,
)


class CheckpointResumeService:
    """
    Restores the latest checkpoint for a crawl session.
    """

    def __init__(
        self,
        *,
        repository: CrawlCheckpointRepository,
    ) -> None:
        self._repository = repository

    async def resume(
        self,
        session_id: str,
    ) -> CrawlCheckpoint | None:
        return await self._repository.get(session_id)
