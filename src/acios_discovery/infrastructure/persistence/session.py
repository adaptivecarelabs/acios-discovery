from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from .database import SessionFactory


@asynccontextmanager
async def session_scope():

    session: AsyncSession = SessionFactory()

    try:

        yield session

        await session.commit()

    except Exception:

        await session.rollback()

        raise

    finally:

        await session.close()
