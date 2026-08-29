from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine

from acios_discovery.api.app import create_app
from acios_discovery.api.dependencies import get_db_session


@pytest_asyncio.fixture
async def api_client(
    test_engine: AsyncEngine,
    test_session_factory,
) -> AsyncGenerator[AsyncClient]:
    """
    An httpx AsyncClient wired directly to the FastAPI app, with
    the app's database dependency overridden to use the isolated
    per-pytest-worker test schema (see tests/conftest.py's
    test_engine fixture) instead of the real database.
    """

    app = create_app()

    async def override_get_db_session():
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(test_session_factory):
    """
    Seeds one active admin user directly via the repository,
    bypassing the API (which requires an existing admin to
    create new users — this fixture provides the first one).
    """

    from acios_discovery.application.auth import hash_password
    from acios_discovery.domain.user import User, UserId, UserRole
    from acios_discovery.infrastructure.persistence.repositories.user_repository import (
        SqlAlchemyUserRepository,
    )

    async with test_session_factory() as session:
        repository = SqlAlchemyUserRepository(session)

        user = User(
            id=UserId.from_sequence(1),
            email="admin@example.com",
            hashed_password=hash_password("admin-password-123"),
            role=UserRole.ADMIN,
        )

        await repository.add(user)
        await session.commit()

    return user


@pytest_asyncio.fixture
async def admin_token(api_client, admin_user) -> str:
    """
    Logs in as the seeded admin user and returns a bearer token.
    """

    response = await api_client.post(
        "/auth/login",
        data={
            "username": "admin@example.com",
            "password": "admin-password-123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


class FakeCrawlingServices:
    """
    Minimal stand-in for CrawlingServices — exposes just the two
    attributes CrawlManager actually touches (.session,
    .publisher) so tests can drive real event flow without a
    real crawl pipeline.
    """

    def __init__(self, session_id: str) -> None:
        from acios_discovery.application.events.in_memory_event_publisher import (
            InMemoryEventPublisher,
        )
        from acios_discovery.domain.crawling.crawl_session import (
            CrawlSession,
        )

        self.session = CrawlSession(id=session_id)
        self.publisher = InMemoryEventPublisher()


class FakeExecutionService:
    """
    Stand-in for DiscoveryExecutionService — completes instantly
    with a small, deterministic result instead of running a real
    crawl. job_count controls how many synthetic
    JobCompletedEvents are published, so SSE-consuming tests have
    something real to observe.

    Persists the CrawlSession's final state via the real
    repository, using the same db_session CrawlManager will
    commit afterward — mirroring what the real
    SessionScopedCrawlSessionPersistence/CrawlSupervisor
    combination does in production, so GET/LIST endpoints (which
    query the database directly) can observe the session.
    """

    def __init__(
        self,
        *,
        session,
        publisher,
        db_session,
        job_count: int = 2,
    ) -> None:
        self._session = session
        self._publisher = publisher
        self._db_session = db_session
        self._job_count = job_count

    async def run(self, *, state: str):
        from acios_discovery.application.discovery.discovery_execution_result import (
            DiscoveryExecutionResult,
        )
        from acios_discovery.domain.crawling.crawl_session_status import (
            CrawlSessionStatus,
        )
        from acios_discovery.domain.crawling.job import CrawlJob
        from acios_discovery.domain.crawling.priority import (
            CrawlPriority,
        )
        from acios_discovery.domain.crawling.status import CrawlStatus
        from acios_discovery.domain.events.job_completed_event import (
            JobCompletedEvent,
        )
        from acios_discovery.domain.sources import Source
        from acios_discovery.infrastructure.persistence.repositories.crawl_session_repository import (
            SqlAlchemyCrawlSessionRepository,
        )

        for i in range(self._job_count):
            job = CrawlJob(
                id=f"fake-job-{i}",
                source=Source.FINELIB,
                listing_url="https://example.test",
                state=state,
                city=f"FakeCity{i}",
                category_slug="fake-category",
                priority=CrawlPriority.NORMAL,
                status=CrawlStatus.COMPLETED,
            )

            await self._publisher.publish(
                JobCompletedEvent(
                    job=job,
                    pages_crawled=1,
                    companies_discovered=3,
                )
            )

        self._session.status = CrawlSessionStatus.COMPLETED
        self._session.jobs_completed = self._job_count
        self._session.pages_crawled = self._job_count
        self._session.companies_discovered = self._job_count * 3

        repository = SqlAlchemyCrawlSessionRepository(self._db_session)
        await repository.save(self._session)

        return DiscoveryExecutionResult(
            session_id=self._session.id,
            resumed=False,
            plans_generated=self._job_count,
            jobs_submitted=self._job_count,
            jobs_processed=self._job_count,
            pages_crawled=self._job_count,
            companies_discovered=self._job_count * 3,
            workers=1,
        )


class FakeDiscoveryServices:
    """
    Stand-in for DiscoveryServices exposing just .crawling and
    .execution_service, matching what CrawlManager touches.
    """

    def __init__(
        self,
        session_id: str,
        *,
        db_session,
        job_count: int = 2,
    ) -> None:
        self.crawling = FakeCrawlingServices(session_id)
        self.execution_service = FakeExecutionService(
            session=self.crawling.session,
            publisher=self.crawling.publisher,
            db_session=db_session,
            job_count=job_count,
        )


@pytest_asyncio.fixture
async def fake_crawl_manager(test_session_factory):
    """
    A CrawlManager wired to the isolated test database and a
    fake crawl pipeline (FakeDiscoveryServices) instead of real
    Finelib/proxy infrastructure. Each started session gets a
    fresh random-looking id and completes near-instantly, firing
    real JobCompletedEvents so SSE and metrics wiring is
    genuinely exercised.
    """

    from uuid import uuid4

    from acios_discovery.api.crawl_manager import CrawlManager

    async def fake_http_client_builder(metrics):
        return None  # never actually used by FakeExecutionService

    async def fake_services_factory(
        *,
        db_session,
        http,
        planner,
        metrics,
        resume_session_id=None,
    ):
        session_id = resume_session_id or str(uuid4())
        return FakeDiscoveryServices(session_id, db_session=db_session)

    return CrawlManager(
        session_factory=test_session_factory,
        http_client_builder=fake_http_client_builder,
        services_factory=fake_services_factory,
    )


@pytest_asyncio.fixture
async def api_client_with_fake_crawls(
    test_engine: AsyncEngine,
    test_session_factory,
    fake_crawl_manager,
):
    """
    Same as api_client, but with the app's crawl_manager
    dependency swapped for one that runs fake crawls — used by
    tests that exercise the crawl-session endpoints without
    needing real Finelib/proxy infrastructure.
    """

    import acios_discovery.api.routers.crawl_sessions as crawl_sessions_module

    app = create_app()

    async def override_get_db_session():
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    original_manager = crawl_sessions_module.crawl_manager
    crawl_sessions_module.crawl_manager = fake_crawl_manager

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            yield client
    finally:
        crawl_sessions_module.crawl_manager = original_manager
        app.dependency_overrides.clear()


class SlowFakeExecutionService(FakeExecutionService):
    """
    Same as FakeExecutionService, but waits on an externally
    controlled asyncio.Event before completing — lets collision-
    protection tests deterministically observe an in-flight
    crawl instead of racing against how fast the fake finishes.
    """

    def __init__(self, *, release_event: asyncio.Event, **kwargs) -> None:
        super().__init__(**kwargs)
        self._release_event = release_event

    async def run(self, *, state: str):
        await self._release_event.wait()
        return await super().run(state=state)


@pytest_asyncio.fixture
async def slow_fake_crawl_manager(test_session_factory):
    """
    Like fake_crawl_manager, but crawls stay "running" until the
    test explicitly releases them via the returned release_event
    — for tests that need to reliably observe an in-flight crawl.
    """

    from uuid import uuid4

    from acios_discovery.api.crawl_manager import CrawlManager

    release_event = asyncio.Event()

    async def fake_http_client_builder(metrics):
        return None

    async def fake_services_factory(
        *,
        db_session,
        http,
        planner,
        metrics,
        resume_session_id=None,
    ):
        session_id = resume_session_id or str(uuid4())
        crawling = FakeCrawlingServices(session_id)

        class _Services:
            def __init__(self) -> None:
                self.crawling = crawling
                self.execution_service = SlowFakeExecutionService(
                    session=crawling.session,
                    publisher=crawling.publisher,
                    db_session=db_session,
                    release_event=release_event,
                )

        return _Services()

    manager = CrawlManager(
        session_factory=test_session_factory,
        http_client_builder=fake_http_client_builder,
        services_factory=fake_services_factory,
    )

    return manager, release_event


@pytest_asyncio.fixture
async def api_client_with_slow_fake_crawls(
    test_engine: AsyncEngine,
    test_session_factory,
    slow_fake_crawl_manager,
):
    """
    Same as api_client_with_fake_crawls, but crawls stay running
    until the test calls release_event.set() — for collision-
    protection tests that need a reliable in-flight window.
    """

    import acios_discovery.api.routers.crawl_sessions as crawl_sessions_module

    manager, release_event = slow_fake_crawl_manager

    app = create_app()

    async def override_get_db_session():
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    original_manager = crawl_sessions_module.crawl_manager
    crawl_sessions_module.crawl_manager = manager

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            yield client, release_event
    finally:
        crawl_sessions_module.crawl_manager = original_manager
        app.dependency_overrides.clear()
