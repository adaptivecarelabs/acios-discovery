from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from .database import SessionFactory


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    """
    Provide one transactional AsyncSession.

    The caller performs all repository operations using
    this session.

    Successful operations are committed.

    Exceptions cause a rollback.
    """

    async with SessionFactory() as session:
        try:
            yield session

            await session.commit()

        except Exception:
            await session.rollback()
            raise
