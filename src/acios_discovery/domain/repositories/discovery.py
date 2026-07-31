from abc import ABC, abstractmethod

from acios_discovery.domain.discovery.record import DiscoveryRecord


class DiscoveryRepository(ABC):
    @abstractmethod
    async def save(
        self,
        record: DiscoveryRecord,
    ) -> None:
        """Persist a discovery record."""

    @abstractmethod
    async def exists(
        self,
        record: DiscoveryRecord,
    ) -> bool:
        """Return True if the record already exists."""

    @abstractmethod
    async def list_all(
        self,
    ) -> list[DiscoveryRecord]:
        """Return every stored record."""
