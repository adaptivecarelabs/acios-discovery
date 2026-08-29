from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from acios_discovery.api.crawl_manager import (
    CrawlAlreadyRunningError,
    crawl_manager,
)
from acios_discovery.api.dependencies import get_current_user, get_db_session
from acios_discovery.api.schemas.crawl_session import (
    CrawlSessionResponse,
    StartCrawlRequest,
)
from acios_discovery.domain.events.job_completed_event import (
    JobCompletedEvent,
)
from acios_discovery.domain.events.job_failed_event import JobFailedEvent
from acios_discovery.domain.user import User
from acios_discovery.infrastructure.persistence.repositories.crawl_session_repository import (
    SqlAlchemyCrawlSessionRepository,
)

router = APIRouter(prefix="/crawl-sessions", tags=["crawl-sessions"])


def _to_response(session) -> CrawlSessionResponse:
    return CrawlSessionResponse(
        id=session.id,
        state=session.state,
        categories=session.categories,
        max_jobs=session.max_jobs,
        triggered_by_user_id=session.triggered_by_user_id,
        status=session.status.value,
        started_at=session.started_at,
        finished_at=session.finished_at,
        jobs_total=session.jobs_total,
        jobs_completed=session.jobs_completed,
        jobs_failed=session.jobs_failed,
        pages_crawled=session.pages_crawled,
        companies_discovered=session.companies_discovered,
    )


@router.post(
    "",
    response_model=CrawlSessionResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_crawl(
    request: StartCrawlRequest,
    user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> CrawlSessionResponse:
    """
    Starts a new crawl session in the background and returns its
    initial (pending) state immediately.
    """

    try:
        session_id = await crawl_manager.start(
            state=request.state,
            categories=request.categories,
            max_jobs=request.max_jobs,
            triggered_by_user_id=user.id.value,
        )

    except CrawlAlreadyRunningError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    repository = SqlAlchemyCrawlSessionRepository(db_session)

    session = await repository.get(session_id)

    if session is not None:
        return _to_response(session)

    # The DB row may not be persisted yet if the background task
    # hasn't reached its first checkpoint — this is expected for
    # a freshly started crawl. Synthesize a pending response from
    # what we already know rather than treating this as an error;
    # the caller can poll GET /crawl-sessions/{id} for real
    # progress shortly after.
    return CrawlSessionResponse(
        id=session_id,
        state=request.state,
        categories=request.categories,
        max_jobs=request.max_jobs,
        triggered_by_user_id=user.id.value,
        status="pending",
        started_at=None,
        finished_at=None,
        jobs_total=0,
        jobs_completed=0,
        jobs_failed=0,
        pages_crawled=0,
        companies_discovered=0,
    )


@router.get("", response_model=list[CrawlSessionResponse])
async def list_crawl_sessions(
    user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> list[CrawlSessionResponse]:

    repository = SqlAlchemyCrawlSessionRepository(db_session)

    sessions = await repository.list_all()

    return [_to_response(s) for s in sessions]


@router.get("/{session_id}", response_model=CrawlSessionResponse)
async def get_crawl_session(
    session_id: str,
    user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> CrawlSessionResponse:

    repository = SqlAlchemyCrawlSessionRepository(db_session)

    session = await repository.get(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such crawl session.",
        )

    return _to_response(session)


@router.post(
    "/{session_id}/resume",
    response_model=CrawlSessionResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def resume_crawl_session(
    session_id: str,
    user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> CrawlSessionResponse:
    """
    Resumes a previously started crawl session using its stored
    scope (state/categories/max_jobs) — no need to re-supply it.
    """

    try:
        await crawl_manager.resume(
            session_id=session_id,
            triggered_by_user_id=user.id.value,
        )

    except CrawlAlreadyRunningError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    repository = SqlAlchemyCrawlSessionRepository(db_session)

    session = await repository.get(session_id)

    return _to_response(session)


@router.get("/{session_id}/events")
async def stream_crawl_events(
    session_id: str,
    user: User = Depends(get_current_user),
):
    """
    Server-Sent Events stream of live progress for a running
    crawl session — one event per completed or failed job.

    Only works while the session is actively running in this
    API server process (see CrawlManager's in-memory-registry
    limitation). Returns 404 if the session isn't currently
    running here.
    """

    running = crawl_manager.get_running(session_id)

    if running is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Session is not currently running in this "
                "server process."
            ),
        )

    queue: asyncio.Queue = asyncio.Queue()

    async def subscriber(event) -> None:
        if isinstance(event, (JobCompletedEvent, JobFailedEvent)):
            await queue.put(
                {
                    "type": type(event).__name__,
                    "city": event.job.city,
                    "category_slug": event.job.category_slug,
                }
            )

    running.publisher.subscribe(subscriber)

    async def event_generator():
        try:
            while True:
                if running.task.done():
                    yield (
                        "event: done\n"
                        "data: {}\n\n"
                    )
                    break

                try:
                    item = await asyncio.wait_for(
                        queue.get(),
                        timeout=5.0,
                    )
                    yield f"data: {json.dumps(item)}\n\n"

                except TimeoutError:
                    yield ": keep-alive\n\n"

        finally:
            running.publisher.unsubscribe(subscriber)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
