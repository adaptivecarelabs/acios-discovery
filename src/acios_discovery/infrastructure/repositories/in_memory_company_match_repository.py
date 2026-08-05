from __future__ import annotations

from acios_discovery.domain.discovery.company_match_repository import (
    CompanyMatchRepository,
)
from acios_discovery.domain.discovery.models import (
    RawDiscovery,
)


class InMemoryCompanyMatchRepository(
    CompanyMatchRepository,
):
    def __init__(self) -> None:
        self._companies: list[RawDiscovery] = []

    async def add(
        self,
        company: RawDiscovery,
    ) -> None:
        self._companies.append(company)

    async def candidates(
        self,
        discovery: RawDiscovery,
    ) -> list[RawDiscovery]:
        return list(self._companies)

    async def list_all(
        self,
    ) -> list[RawDiscovery]:
        return list(self._companies)
