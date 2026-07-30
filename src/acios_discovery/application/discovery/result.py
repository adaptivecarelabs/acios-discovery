from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class DiscoveryRunResult:
    source: str

    records_found: int

    records_saved: int

    duplicates: int = 0

    errors: list[str] = field(default_factory=list)
