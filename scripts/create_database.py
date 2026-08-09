import asyncio

#
# IMPORTANT
#
from acios_discovery.infrastructure.persistence.database import (
    engine,
)
from acios_discovery.infrastructure.persistence.metadata import (
    Base,
)


async def create_database():

    async with engine.begin() as conn:

        await conn.run_sync(
            Base.metadata.create_all,
        )

    print()

    print("=" * 60)

    print("DATABASE CREATED")

    print("=" * 60)

    print()

    print("Tables:")

    for table in Base.metadata.tables:

        print(" -", table)


if __name__ == "__main__":

    asyncio.run(
        create_database(),
    )
