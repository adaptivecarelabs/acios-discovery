from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
)
from acios_discovery.application.planning.crawl_plan_generator import (
    CrawlPlanGenerator,
)
from acios_discovery.application.planning.filtered_crawl_plan_generator import (
    FilteredCrawlPlanGenerator,
)
from acios_discovery.application.planning.providers.category_provider import (
    CategoryProvider,
)
from acios_discovery.application.planning.providers.city_provider import (
    CityProvider,
)
from acios_discovery.application.proxy import AdaptiveProxyPool
from acios_discovery.bootstrap.discovery_services import DiscoveryServices
from acios_discovery.domain.crawling.crawl_session_status import (
    CrawlSessionStatus,
)
from acios_discovery.domain.http import HttpClient
from acios_discovery.infrastructure.http.httpx_client import HttpxClient
from acios_discovery.infrastructure.http.proxy_rotating_http_client import (
    ProxyRotatingHttpClient,
)
from acios_discovery.infrastructure.persistence.config import WEBSHARE_API_KEY
from acios_discovery.infrastructure.persistence.database import (
    SessionFactory,
)
from acios_discovery.infrastructure.persistence.repositories.crawl_session_repository import (
    SqlAlchemyCrawlSessionRepository,
)
from acios_discovery.shared.logging import logger

# A services_factory builds the object CrawlManager actually drives:
# anything exposing .crawling.session (a CrawlSession), .crawling.publisher
# (an event publisher with subscribe/unsubscribe), and
# .execution_service.run(state=...). Production uses the real
# DiscoveryServices; tests can substitute a lightweight fake.
ServicesFactory = Callable[..., Awaitable[object]]

HttpClientBuilder = Callable[[CrawlMetricsService], Awaitable[HttpClient]]


class CrawlAlreadyRunningError(Exception):
    """
    Raised when starting or resuming a session that already has
    a live background task in this process, or whose DB row
    still shows RUNNING from an untracked source (e.g. a prior
    server instance that hasn't been reconciled yet — see
    reconcile_orphaned_sessions).
    """


class RunningCrawl:
    """
    Tracks one crawl session's live, in-process state — its
    background task, the event publisher/metrics it's using (so
    an SSE endpoint can subscribe to live progress and a status
    endpoint can report the latest snapshot even before the DB
    row is updated), and its scope (so start() can detect and
    reject an overlapping crawl before launching a duplicate).
    """

    def __init__(
        self,
        *,
        task: asyncio.Task,
        publisher,
        metrics: CrawlMetricsService,
        state: str,
        categories: list[str] | None,
    ) -> None:
        self.task = task
        self.publisher = publisher
        self.metrics = metrics
        self.state = state
        self.categories = categories


async def _default_build_http_client(
    metrics: CrawlMetricsService,
) -> HttpClient:

    if not WEBSHARE_API_KEY:
        return HttpxClient()

    from acios_discovery.infrastructure.proxy import (
        WebshareProxyProvider,
    )

    provider = WebshareProxyProvider(api_key=WEBSHARE_API_KEY)

    proxies = await provider.list_proxies()

    if not proxies:
        return HttpxClient()

    pool = AdaptiveProxyPool(proxies)

    return ProxyRotatingHttpClient(
        inner=HttpxClient(),
        pool=pool,
        metrics=metrics,
    )


async def _default_build_services(
    *,
    db_session,
    http: HttpClient,
    planner,
    metrics: CrawlMetricsService,
    resume_session_id: str | None = None,
) -> DiscoveryServices:

    return DiscoveryServices(
        session=db_session,
        workers=1,
        http=http,
        planner=planner,
        metrics=metrics,
        resume_session_id=resume_session_id,
    )


class CrawlManager:
    """
    Starts and tracks crawl sessions running as background
    asyncio tasks within this API server process.

    This is an in-memory registry: it only knows about crawls
    started by this process instance. If the API server
    restarts, a crawl's DB row still reflects its last
    checkpointed progress (same durability guarantees the CLI
    has always had), but the live task/publisher reference is
    gone. Call reconcile_orphaned_sessions() once at startup so
    those DB rows don't linger at RUNNING forever.

    session_factory and services_factory are injectable so tests
    can substitute an isolated test database and a fake crawl
    execution, without needing real Finelib/proxy infrastructure
    or the real (much slower) discovery pipeline.
    """

    def __init__(
        self,
        *,
        session_factory: Callable[[], object] = SessionFactory,
        http_client_builder: HttpClientBuilder = (
            _default_build_http_client
        ),
        services_factory: ServicesFactory = _default_build_services,
    ) -> None:
        self._running: dict[str, RunningCrawl] = {}
        self._session_factory = session_factory
        self._build_http_client = http_client_builder
        self._build_services = services_factory
        self._lock = asyncio.Lock()

    def get_running(
        self,
        session_id: str,
    ) -> RunningCrawl | None:
        return self._running.get(session_id)

    def _make_planner(
        self,
        *,
        categories: list[str] | None,
        max_jobs: int | None,
    ):
        return FilteredCrawlPlanGenerator(
            inner=CrawlPlanGenerator(
                city_provider=CityProvider(),
                category_provider=CategoryProvider(),
            ),
            categories=categories,
            max_jobs=max_jobs,
        )

    async def _launch(
        self,
        *,
        state: str,
        categories: list[str] | None,
        max_jobs: int | None,
        triggered_by_user_id: str,
        resume_session_id: str | None,
    ) -> str:
        """
        Shared implementation behind start() and resume(): builds
        a fresh DiscoveryServices bound to its own db_session, and
        launches its execution as a tracked background task.

        db_session's whole lifetime is scoped to run(), including
        acquisition — this guarantees the connection is released
        exactly once, on every exit path (success, failure, or an
        exception raised before execution_service.run() is even
        reached), which a manual __aenter__()/close() pair does
        not guarantee as cleanly.
        """

        metrics = CrawlMetricsService()

        http = await self._build_http_client(metrics)

        planner = self._make_planner(
            categories=categories,
            max_jobs=max_jobs,
        )

        # A holder so the outer function can read the id that
        # run() establishes once it enters the session context.
        session_id_holder: dict[str, str] = {}
        publisher_holder: dict[str, object] = {}
        started = asyncio.Event()

        async def run() -> None:
            try:
                async with self._session_factory() as db_session:

                    services = await self._build_services(
                        db_session=db_session,
                        http=http,
                        planner=planner,
                        metrics=metrics,
                        resume_session_id=resume_session_id,
                    )

                    session_id = services.crawling.session.id

                    services.crawling.session.state = state
                    services.crawling.session.categories = categories
                    services.crawling.session.max_jobs = max_jobs
                    services.crawling.session.triggered_by_user_id = (
                        triggered_by_user_id
                    )

                    session_id_holder["id"] = session_id
                    publisher_holder["publisher"] = (
                        services.crawling.publisher
                    )
                    started.set()

                    try:
                        await services.execution_service.run(
                            state=state,
                        )
                        await db_session.commit()

                    except Exception:
                        logger.exception(
                            "Crawl session %s failed unexpectedly",
                            session_id,
                        )
                        await db_session.rollback()

            finally:
                session_id = session_id_holder.get("id")
                if session_id is not None:
                    self._running.pop(session_id, None)

        task = asyncio.create_task(run())

        # Wait for run() to reach the point where the session id
        # is known, so this method can return it — but no longer,
        # since the crawl itself must keep running in the
        # background rather than being awaited here.
        await started.wait()

        session_id = session_id_holder["id"]

        self._running[session_id] = RunningCrawl(
            task=task,
            publisher=publisher_holder["publisher"],
            metrics=metrics,
            state=state,
            categories=categories,
        )

        return session_id

    def _scope_key(
        self,
        *,
        state: str,
        categories: list[str] | None,
    ) -> tuple[str, tuple[str, ...] | None]:
        """
        A hashable identity for "what this crawl covers", used to
        detect overlapping in-flight crawls. Categories are
        sorted so equivalent requests (e.g. ["a", "b"] vs
        ["b", "a"]) are recognized as the same scope.
        """
        return (
            state,
            tuple(sorted(categories)) if categories else None,
        )

    def _find_running_with_same_scope(
        self,
        *,
        state: str,
        categories: list[str] | None,
    ) -> str | None:

        target = self._scope_key(state=state, categories=categories)

        for session_id, running in self._running.items():
            running_scope = self._scope_key(
                state=running.state,
                categories=running.categories,
            )
            if running_scope == target:
                return session_id

        return None

    async def start(
        self,
        *,
        state: str,
        categories: list[str] | None,
        max_jobs: int | None,
        triggered_by_user_id: str,
    ) -> str:
        """
        Starts a new crawl session as a background task and
        returns its session id immediately — this call does not
        wait for the crawl to finish.

        Raises CrawlAlreadyRunningError if a crawl with the same
        (state, categories) scope is already running in this
        process — prevents two people from independently
        triggering overlapping crawls that would waste proxy
        budget and race each other's writes.
        """

        async with self._lock:

            conflicting_id = self._find_running_with_same_scope(
                state=state,
                categories=categories,
            )

            if conflicting_id is not None:
                raise CrawlAlreadyRunningError(
                    f"A crawl for state={state!r} "
                    f"categories={categories!r} is already "
                    f"running (session {conflicting_id}). Wait "
                    "for it to finish, or use a narrower scope."
                )

            return await self._launch(
                state=state,
                categories=categories,
                max_jobs=max_jobs,
                triggered_by_user_id=triggered_by_user_id,
                resume_session_id=None,
            )

    async def resume(
        self,
        *,
        session_id: str,
        triggered_by_user_id: str,
    ) -> str:
        """
        Resumes a previously started session, using the scope
        (state/categories/max_jobs) stored on that session's DB
        row — the caller does not need to re-supply it.

        Raises CrawlAlreadyRunningError if this session already
        has a live task in this process, or if its DB row still
        shows RUNNING from a source this process doesn't know
        about (most likely a prior server instance that crashed
        or restarted without reconciliation — call
        reconcile_orphaned_sessions() at startup to prevent this
        from lingering indefinitely).
        """

        async with self._lock:

            if session_id in self._running:
                raise CrawlAlreadyRunningError(
                    f"Session {session_id} is already running "
                    "in this process.",
                )

            async with self._session_factory() as lookup_session:
                repository = SqlAlchemyCrawlSessionRepository(
                    lookup_session,
                )

                existing = await repository.get(session_id)

            if existing is None:
                raise ValueError(
                    f"No such session: {session_id}",
                )

            if existing.status == CrawlSessionStatus.RUNNING:
                raise CrawlAlreadyRunningError(
                    f"Session {session_id} is marked RUNNING but "
                    "is not tracked by this process. If the API "
                    "server restarted while it was running, wait "
                    "for startup reconciliation to mark it "
                    "CANCELLED, then resume again.",
                )

            if existing.state is None:
                raise ValueError(
                    f"Session {session_id} has no stored scope "
                    "and cannot be resumed automatically.",
                )

            return await self._launch(
                state=existing.state,
                categories=existing.categories,
                max_jobs=existing.max_jobs,
                triggered_by_user_id=triggered_by_user_id,
                resume_session_id=session_id,
            )


async def reconcile_orphaned_sessions(
    *,
    session_factory: Callable[[], object] = SessionFactory,
) -> int:
    """
    Marks every session still showing RUNNING as CANCELLED.

    Call once at API server startup, before accepting traffic.
    A session can only legitimately be RUNNING while a live
    background task in some process is driving it; since a fresh
    server process starts with an empty CrawlManager registry,
    any RUNNING row at startup is necessarily orphaned — left
    over from a previous process that stopped without reaching
    its own completion/failure handling (e.g. killed, crashed,
    or the machine restarted).

    Returns the number of sessions reconciled.
    """

    async with session_factory() as db_session:

        repository = SqlAlchemyCrawlSessionRepository(db_session)

        sessions = await repository.list_all()

        orphaned = [
            s
            for s in sessions
            if s.status == CrawlSessionStatus.RUNNING
        ]

        for session in orphaned:
            session.status = CrawlSessionStatus.CANCELLED
            await repository.save(session)

            logger.warning(
                "Reconciled orphaned crawl session %s "
                "(was RUNNING, marked CANCELLED at startup).",
                session.id,
            )

        await db_session.commit()

        return len(orphaned)


crawl_manager = CrawlManager()
