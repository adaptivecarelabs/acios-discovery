import pytest

from acios_discovery.application.crawling.resume.checkpoint_resume_service import (
    CheckpointResumeService,
)
from acios_discovery.domain.crawling.crawl_checkpoint import (
    CrawlCheckpoint,
)
from acios_discovery.infrastructure.repositories.in_memory_crawl_checkpoint_repository import (
    InMemoryCrawlCheckpointRepository,
)


@pytest.mark.asyncio
async def test_resume_returns_checkpoint():

    repository = InMemoryCrawlCheckpointRepository()

    checkpoint = CrawlCheckpoint(
        session_id="session-1",
        state="Lagos",
        city="Yaba",
        category_slug="restaurants",
        page=12,
        company_index=4,
    )

    await repository.save(checkpoint)

    service = CheckpointResumeService(
        repository=repository,
    )

    restored = await service.resume(
        "session-1",
    )

    assert checkpoint.company_index == 4
    assert restored is checkpoint


@pytest.mark.asyncio
async def test_resume_returns_none_when_missing():

    repository = InMemoryCrawlCheckpointRepository()

    service = CheckpointResumeService(
        repository=repository,
    )

    restored = await service.resume(
        "missing",
    )

    assert restored is None
