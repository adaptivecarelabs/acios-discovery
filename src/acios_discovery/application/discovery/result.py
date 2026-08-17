from __future__ import annotations

from dataclasses import dataclass, field

from acios_discovery.domain.discovery.record import (
    DiscoveryRecord,
)


@dataclass(slots=True, frozen=True)
class DiscoveryRunResult:
    """
    Result of processing one complete discovery execution.
    """

    source: str

    pages_crawled: int = 0
    records_found: int = 0
    records_saved: int = 0
    duplicates: int = 0

    records: list[DiscoveryRecord] = field(
        default_factory=list,
    )

    errors: list[str] = field(
        default_factory=list,
    )

    @property
    def companies_discovered(self) -> int:
        """
        Compatibility alias for discovery terminology.
        """
        return self.records_found

    @property
    def successful(self) -> bool:
        """
        Return True when the discovery run completed
        without recorded errors.
        """
        return not self.errors
