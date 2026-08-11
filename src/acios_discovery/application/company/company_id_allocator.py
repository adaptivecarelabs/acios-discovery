from __future__ import annotations

from abc import ABC, abstractmethod

from acios_discovery.domain.company.company_id import CompanyId


class CompanyIdAllocator(ABC):
    """
    Allocates globally unique Company identifiers.
    """

    @abstractmethod
    async def allocate(self) -> CompanyId:
        """
        Allocate the next CompanyId.
        """
        ...
