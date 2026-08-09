from __future__ import annotations

from acios_discovery.domain.discovery import (
    DiscoveryRepository,
)
from acios_discovery.domain.discovery.record import DiscoveryRecord


class InMemoryDiscoveryRepository(
    DiscoveryRepository,
):

    def __init__(self) -> None:

        self._records: dict[
            str,
            DiscoveryRecord,
        ] = {}

    def _key(
        self,
        record: DiscoveryRecord,
    ) -> str:

        if record.company.detail_url is None:
            raise ValueError(
                "Discovery has no detail URL."
        )

        return record.company.detail_url

    async def save(
        self,
        record: DiscoveryRecord,
    ) -> None:

        self._records[
            self._key(record)
        ] = record

    async def update(
        self,
        record: DiscoveryRecord,
    ) -> None:

        self._records[
            self._key(record)
        ] = record

    async def exists(
        self,
        record: DiscoveryRecord,
    ) -> bool:

        return self._key(record) in self._records

    async def list_all(
        self,
    ) -> list[DiscoveryRecord]:

        return list(
            self._records.values()
        )

    async def count(
        self,
    ) -> int:

        return len(
            self._records
        )

    async def clear(
        self,
    ) -> None:

        self._records.clear()
