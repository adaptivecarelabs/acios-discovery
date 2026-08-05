from __future__ import annotations

from dataclasses import dataclass

from acios_discovery.application.resolution.entity_match import (
    EntityMatch,
)


@dataclass(slots=True)
class ResolutionScore:
    """
    Final score produced by the
    entity resolution engine.
    """

    score: float

    decision: EntityMatch
