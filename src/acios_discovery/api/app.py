from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from acios_discovery.api.crawl_manager import reconcile_orphaned_sessions
from acios_discovery.api.routers import auth, crawl_sessions, users
from acios_discovery.shared.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):

    reconciled_count = await reconcile_orphaned_sessions()

    if reconciled_count:
        logger.warning(
            "Startup: reconciled %d orphaned crawl session(s) "
            "left RUNNING by a previous process.",
            reconciled_count,
        )

    yield


def create_app() -> FastAPI:

    app = FastAPI(
        title="Acios Discovery API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.include_router(auth.router)
    app.include_router(crawl_sessions.router)
    app.include_router(users.router)

    return app


app = create_app()
