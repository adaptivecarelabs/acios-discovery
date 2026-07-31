from acios_discovery.domain.discovery.record import DiscoveryRecord
from acios_discovery.domain.repositories.discovery_repository import (
    DiscoveryRepository,
)


class InMemoryDiscoveryRepository(
    DiscoveryRepository,
):
    """
    Simple in-memory repository used for testing.
    """

    def __init__(self) -> None:
        self._records: list[
            DiscoveryRecord
        ] = []

    async def save(
        self,
        record: DiscoveryRecord,
    ) -> None:

        if not await self.exists(record):
            self._records.append(record)

    async def exists(
        self,
        record: DiscoveryRecord,
    ) -> bool:

        return record in self._records

    async def list_all(
        self,
    ) -> list[DiscoveryRecord]:

        return list(self._records)

    async def count(
        self,
    ) -> int:

        return len(self._records)

    async def clear(
        self,
    ) -> None:

        self._records.clear()
