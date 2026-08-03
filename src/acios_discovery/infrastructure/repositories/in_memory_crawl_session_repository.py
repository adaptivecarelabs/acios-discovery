from acios_discovery.domain.crawling.crawl_session import CrawlSession
from acios_discovery.domain.repositories.crawl_session_repository import (
    CrawlSessionRepository,
)


class InMemoryCrawlSessionRepository(
    CrawlSessionRepository,
):
    def __init__(self) -> None:
        self._sessions: dict[str, CrawlSession] = {}

    async def save(
        self,
        session: CrawlSession,
    ) -> None:
        self._sessions[session.id] = session

    async def get(
        self,
        session_id: str,
    ) -> CrawlSession | None:
        return self._sessions.get(session_id)

    async def list_all(
        self,
    ) -> list[CrawlSession]:
        return list(self._sessions.values())

    async def delete(
        self,
        session_id: str,
    ) -> None:
        self._sessions.pop(session_id, None)
