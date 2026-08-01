from dataclasses import dataclass

from .record import DiscoveryRecord


@dataclass(slots=True)
class DiscoveryPage:
    records: list[DiscoveryRecord]
    next_page_url: str | None
