from __future__ import annotations

from abc import ABC, abstractmethod

from acios_discovery.domain.discovery.models import RawDiscovery


class CompanyMatchRepository(ABC):
    """
    Repository used by the entity
    resolution engine to retrieve
    potential duplicate companies.
    """

    @abstractmethod
    async def candidates(
        self,
        discovery: RawDiscovery,
    ) -> list[RawDiscovery]:
        """
        Return possible duplicate
        candidates.

        Implementations may search
        by

        - name
        - website
        - email
        - phone
        - city
        """
