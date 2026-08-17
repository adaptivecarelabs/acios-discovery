import os
from collections.abc import AsyncGenerator, Callable, Mapping
from pathlib import Path

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from acios_discovery.domain.discovery.context import DiscoveryContext
from acios_discovery.domain.discovery.models import RawDiscovery
from acios_discovery.domain.discovery.record import DiscoveryRecord
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.persistence import orm  # noqa: F401
from acios_discovery.infrastructure.persistence.metadata import Base

#
# Test environment
#

load_dotenv(".env.test")


class FixtureHttpClient:
    """
    Deterministic HTTP client backed by in-memory HTML fixtures.

    The client never performs real HTTP requests.

    Tests register a mapping of URL -> HTML content and the
    client returns the corresponding fixture for each request.
    """

    def __init__(
        self,
        pages: Mapping[str, str],
    ) -> None:
        self._pages = dict(pages)
        self.requests: list[str] = []

    async def get(
        self,
        url: str,
    ) -> str:
        self.requests.append(url)

        if url not in self._pages:
            raise AssertionError(
                f"No fixture registered for URL: {url}"
            )

        return self._pages[url]



#
# Discovery fixtures
#


@pytest.fixture
def discovery_record() -> DiscoveryRecord:
    return DiscoveryRecord(
        context=DiscoveryContext(
            source=Source.FINELIB,
            state="Lagos",
            city="Lagos",
            category="Healthcare",
            listing_url="https://www.finelib.com",
        ),
        company=RawDiscovery(
            source="finelib",
            business_name="Drugstoc EHub Ltd",
            detail_url="https://example.com/company",
            address="Ikeja, Lagos",
            phone_numbers=[
                "08030000000",
            ],
            description="Healthcare company",
        ),
    )


#
# Finelib fixtures
#


@pytest.fixture
def finelib_health_fixture() -> str:
    fixture = (
        Path(__file__).parent
        / "fixtures"
        / "finelib"
        / "lagos_healthcare_services.html"
    )

    return fixture.read_text(
        encoding="utf-8",
    )


@pytest.fixture
def finelib_single_health_fixture() -> str:
    fixture = (
        Path(__file__).parent
        / "fixtures"
        / "finelib"
        / "lagos_healthcare_single.html"
    )

    return fixture.read_text(
        encoding="utf-8",
    )


@pytest.fixture
def finelib_detail_fixture() -> str:
    fixture = (
        Path(__file__).parent
        / "fixtures"
        / "finelib"
        / "detail"
        / "phytoscience_double_stem_cell.html"
    )

    return fixture.read_text(
        encoding="utf-8",
    )


def load_fixture(path: str) -> str:
    return Path(path).read_text(
        encoding="utf-8",
    )


@pytest.fixture
def lagos_agriculture_service_page1() -> str:
    return load_fixture(
        "tests/fixtures/finelib/pagination/"
        "lagos_agriculture_service_page1.html"
    )


@pytest.fixture
def lagos_agriculture_service_page2() -> str:
    return load_fixture(
        "tests/fixtures/finelib/pagination/"
        "lagos_agriculture_service_page2.html"
    )


@pytest.fixture
def finelib_food_fixture() -> str:
    return load_fixture(
        "tests/fixtures/finelib/"
        "lagos_food_services.html"
    )


@pytest.fixture
def finelib_restaurants_fixture() -> str:
    return load_fixture(
        "tests/fixtures/finelib/"
        "lagos_restaurant_services.html"
    )


@pytest.fixture
def fixture_http_client():
    """
    Factory for deterministic fixture-backed HTTP clients.

    Tests provide a mapping of URL -> fixture HTML.
    """

    def create(
        pages: Mapping[str, str],
    ) -> FixtureHttpClient:
        return FixtureHttpClient(pages)

    return create


#
# Database fixtures
#


@pytest_asyncio.fixture
async def test_engine(
    worker_id: str,
) -> AsyncGenerator[AsyncEngine]:
    """
    Create an isolated PostgreSQL engine for one pytest worker.

    pytest-xdist assigns each worker a unique worker_id:

        master
        gw0
        gw1
        gw2
        gw3
        ...

    Each worker receives its own PostgreSQL schema inside the
    dedicated acios_discovery_test database.

    This prevents parallel pytest workers from dropping,
    creating, or querying the same tables concurrently.
    """

    database_url = os.getenv(
        "TEST_DATABASE_URL",
    )

    if not database_url:
        raise RuntimeError(
            "TEST_DATABASE_URL must be set before "
            "running persistence or integration tests.",
        )

    if "acios_discovery_test" not in database_url:
        raise RuntimeError(
            "TEST_DATABASE_URL must point to the "
            "acios_discovery_test database.",
        )

    #
    # PostgreSQL schema names cannot contain arbitrary characters.
    # pytest-xdist worker IDs are currently master/gw0/gw1/etc.,
    # but we normalize defensively.
    #

    safe_worker_id = "".join(
        character
        if character.isalnum() or character == "_"
        else "_"
        for character in worker_id
    )

    schema_name = (
        f"acios_test_{safe_worker_id}"
    )

    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
        poolclass=NullPool,
        connect_args={
            "server_settings": {
                "search_path": (
                    f'"{schema_name}",public'
                ),
            },
        },
    )

    try:
        async with engine.begin() as connection:
            #
            # Create this worker's private schema.
            #
            await connection.exec_driver_sql(
                f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"',
            )

            #
            # Explicitly establish the schema for this
            # connection before SQLAlchemy creates metadata.
            #
            await connection.exec_driver_sql(
                f'SET search_path TO "{schema_name}", public',
            )

            #
            # Completely reset ONLY this worker's schema.
            #
            await connection.exec_driver_sql(
                f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE',
            )

            await connection.exec_driver_sql(
                f'CREATE SCHEMA "{schema_name}"',
            )

            await connection.exec_driver_sql(
                f'SET search_path TO "{schema_name}", public',
            )

            #
            # Create every ORM table registered with Base.metadata.
            #
            await connection.run_sync(
                Base.metadata.create_all,
            )

        yield engine

    finally:
        #
        # Remove ONLY this worker's schema.
        #
        async with engine.begin() as connection:
            await connection.exec_driver_sql(
                f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE',
            )

        await engine.dispose()


@pytest.fixture
def test_session_factory(
    test_engine: AsyncEngine,
) -> Callable[[], AsyncSession]:
    """
    Provide a session factory bound to the isolated
    pytest-worker database schema.
    """

    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture
async def db_session(
    test_session_factory: Callable[[], AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    """
    Provide a fresh database session for each test.

    The underlying engine is already isolated to the
    current pytest-xdist worker schema.
    """

    async with test_session_factory() as session:
        try:
            yield session

        finally:
            await session.rollback()
