from __future__ import annotations

from dataclasses import dataclass

from acios_discovery.domain.company.company import Company


@dataclass(
    slots=True,
)
class ResolutionResult:

    """
    Result of entity resolution.

    If duplicate=True,
    company refers to the existing Company aggregate.

    Otherwise company is None.
    """

    company: Company | None

    confidence: float

    duplicate: bool
