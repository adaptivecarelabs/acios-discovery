from __future__ import annotations

from acios_discovery.application.company.company_id_allocator import (
    CompanyIdAllocator,
)
from acios_discovery.domain.company.company_id import CompanyId


class SequentialCompanyIdAllocator(CompanyIdAllocator):
    """
    In-memory sequential CompanyId allocator.

    Intended initially for application wiring and tests.
    Production persistence-backed allocation will replace this.
    """

    def __init__(
        self,
        *,
        starting_sequence: int = 1,
    ) -> None:
        if starting_sequence < 1:
            raise ValueError(
                "starting_sequence must be positive",
            )

        self._sequence = starting_sequence

    async def allocate(self) -> CompanyId:
        company_id = CompanyId.from_sequence(
            self._sequence,
        )

        self._sequence += 1

        return company_id
