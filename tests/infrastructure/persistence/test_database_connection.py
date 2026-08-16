import pytest
from sqlalchemy import text

from acios_discovery.infrastructure.persistence.database import (
    SessionFactory,
)


@pytest.mark.asyncio
async def test_database_connection():
    async with SessionFactory() as session:
        result = await session.execute(
            text("SELECT 1")
        )

        assert result.scalar_one() == 1
