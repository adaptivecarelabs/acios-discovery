from acios_discovery.domain.crawling.crawl_session import (
    CrawlSession,
)
from acios_discovery.domain.crawling.crawl_session_status import (
    CrawlSessionStatus,
)
from acios_discovery.infrastructure.persistence.repositories.crawl_session_repository import (
    SqlAlchemyCrawlSessionRepository,
)


async def test_crawl_session_repository_save_and_get(
    db_session,
):
    repository = SqlAlchemyCrawlSessionRepository(
        db_session,
    )

    session = CrawlSession()

    await repository.save(session)
    await db_session.commit()

    loaded = await repository.get(
        session.id,
    )

    assert loaded is not None
    assert loaded.id == session.id
    assert loaded.status == CrawlSessionStatus.PENDING


async def test_crawl_session_repository_updates_existing_session(
    db_session,
):
    repository = SqlAlchemyCrawlSessionRepository(
        db_session,
    )

    session = CrawlSession()

    await repository.save(session)
    await db_session.commit()

    session.start()

    await repository.save(session)
    await db_session.commit()

    loaded = await repository.get(
        session.id,
    )

    assert loaded is not None
    assert loaded.status == CrawlSessionStatus.RUNNING
    assert loaded.started_at is not None
