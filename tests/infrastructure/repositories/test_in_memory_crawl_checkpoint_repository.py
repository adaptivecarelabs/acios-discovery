import pytest

from acios_discovery.domain.crawling.crawl_checkpoint import (
    CrawlCheckpoint,
)
from acios_discovery.infrastructure.repositories.in_memory_crawl_checkpoint_repository import (
    InMemoryCrawlCheckpointRepository,
)


@pytest.mark.asyncio
async def test_checkpoint_repository_crud():

    repo = InMemoryCrawlCheckpointRepository()

    checkpoint = CrawlCheckpoint(
        session_id="abc",
        state="Lagos",
        city="Yaba",
        category_slug="restaurants",
        page=7,
    )

    await repo.save(checkpoint)

    loaded = await repo.get("abc")

    assert loaded is not None

    assert loaded.page == 7

    await repo.delete("abc")

    assert await repo.get("abc") is None
