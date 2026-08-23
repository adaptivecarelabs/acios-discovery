from __future__ import annotations

from abc import ABC, abstractmethod

from acios_discovery.domain.company.company import Company
from acios_discovery.domain.discovery.models import RawDiscovery


class CompanyMatchRepository(ABC):
    """
    Returns a bounded candidate set of companies that might be
    the same real-world entity as an incoming discovery.

    This exists so EntityResolutionEngine's fuzzy scoring never
    has to scan the entire company registry: implementations
    narrow the search using exact-match signals (name, alias,
    phone, email, website) and geography (city/state), and the
    engine then scores fuzzy similarity only within that bounded
    set.
    """

    @abstractmethod
    async def candidates(
        self,
        discovery: RawDiscovery,
    ) -> list[Company]:
        """
        Return possible duplicate candidates for this discovery.
        """
