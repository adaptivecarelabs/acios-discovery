from __future__ import annotations

from datetime import datetime

from acios_discovery.domain.company.company_id import CompanyId
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

        self._resolutions: dict[
            str,
            tuple[CompanyId, datetime],
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

        key = self._key(record)

        if key not in self._records:
            raise ValueError(
                "Discovery record does not exist: "
                f"{record.company.business_name}"
            )

        self._records[key] = record

    async def resolve(
        self,
        record: DiscoveryRecord,
        company_id: CompanyId,
        resolved_at: datetime,
    ) -> None:

        key = self._key(record)

        if key not in self._records:
            raise ValueError(
                "Discovery does not exist: "
                f"{record.company.business_name}"
            )

        self._resolutions[key] = (
            company_id,
            resolved_at,
        )

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
        self._resolutions.clear()
