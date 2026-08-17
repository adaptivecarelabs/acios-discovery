from abc import ABC, abstractmethod
from datetime import datetime

from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.domain.discovery.record import DiscoveryRecord


class DiscoveryRepository(ABC):
    """
    Repository abstraction for discovered companies.
    """

    @abstractmethod
    async def save(
        self,
        record: DiscoveryRecord,
    ) -> None:
        ...

    @abstractmethod
    async def update(
        self,
        record: DiscoveryRecord,
    ) -> None:
        ...

    @abstractmethod
    async def resolve(
        self,
        record: DiscoveryRecord,
        company_id: CompanyId,
        resolved_at: datetime,
    ) -> None:
        """
        Associate a persisted discovery with its canonical company.
        """
        ...

    @abstractmethod
    async def exists(
        self,
        record: DiscoveryRecord,
    ) -> bool:
        ...

    @abstractmethod
    async def list_all(
        self,
    ) -> list[DiscoveryRecord]:
        ...

    @abstractmethod
    async def count(
        self,
    ) -> int:
        ...

    @abstractmethod
    async def clear(
        self,
    ) -> None:
        ...
