from __future__ import annotations

from dataclasses import dataclass

from acios_discovery.application.resolution.entity_match import EntityMatch
from acios_discovery.domain.company.company import Company


@dataclass(
    slots=True,
)
class ResolutionResult:
    """
    Result of entity resolution.

    company is the best candidate found, if any.

    match describes the resolution outcome.
    """

    company: Company | None

    confidence: float

    match: EntityMatch

    @property
    def duplicate(self) -> bool:
        """
        Backward-compatible indication that the
        incoming discovery should be merged.
        """
        return self.match in {
            EntityMatch.SAME,
            EntityMatch.STRONG_MATCH,
        }
