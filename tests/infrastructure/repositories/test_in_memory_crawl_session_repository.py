import pytest

from acios_discovery.domain.crawling.crawl_session import (
    CrawlSession,
)
from acios_discovery.infrastructure.repositories.in_memory_crawl_session_repository import (
    InMemoryCrawlSessionRepository,
)


@pytest.mark.asyncio
async def test_repository_crud_operations():

    repository = InMemoryCrawlSessionRepository()

    session = CrawlSession(
        id="session-001",
    )

    # Save
    await repository.save(
        session,
    )

    # Get
    loaded = await repository.get(
        "session-001",
    )

    assert loaded is session

    # List
    sessions = await repository.list_all()

    assert len(sessions) == 1

    assert sessions[0].id == "session-001"

    # Delete
    await repository.delete(
        "session-001",
    )

    assert await repository.get(
        "session-001",
    ) is None

    assert await repository.list_all() == []
