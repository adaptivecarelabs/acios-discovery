from abc import ABC, abstractmethod

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
