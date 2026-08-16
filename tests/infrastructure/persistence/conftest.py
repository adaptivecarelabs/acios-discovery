import os
from collections.abc import AsyncGenerator

import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from acios_discovery.infrastructure.persistence import orm  # noqa: F401
from acios_discovery.infrastructure.persistence.metadata import Base

# Load test-specific environment variables before the fixtures
# attempt to read TEST_DATABASE_URL.
load_dotenv(".env.test")


@pytest_asyncio.fixture
async def test_engine() -> AsyncGenerator[AsyncEngine]:
    """
    Create an isolated PostgreSQL engine for one persistence test.

    The engine is intentionally function-scoped so that its
    connection pool never survives across pytest event loops.
    """

    database_url = os.getenv(
        "TEST_DATABASE_URL",
    )

    if not database_url:
        raise RuntimeError(
            "TEST_DATABASE_URL must be set before "
            "running persistence tests.",
        )

    if "acios_discovery_test" not in database_url:
        raise RuntimeError(
            "TEST_DATABASE_URL must point to the "
            "acios_discovery_test database.",
        )

    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
        poolclass=NullPool,
    )

    try:
        async with engine.begin() as connection:
            await connection.run_sync(
                Base.metadata.drop_all,
            )

            await connection.run_sync(
                Base.metadata.create_all,
            )

        yield engine

    finally:
        async with engine.begin() as connection:
            await connection.run_sync(
                Base.metadata.drop_all,
            )

        await engine.dispose()


@pytest_asyncio.fixture
async def db_session(
    test_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession]:
    """
    Provide a fresh database session for each test.
    """

    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        try:
            yield session

        finally:
            await session.rollback()
