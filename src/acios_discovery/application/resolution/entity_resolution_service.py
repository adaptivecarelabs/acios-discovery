from __future__ import annotations

from acios_discovery.application.resolution.entity_match import EntityMatch
from acios_discovery.application.resolution.entity_resolution_engine import (
    EntityResolutionEngine,
)
from acios_discovery.application.resolution.resolution_result import (
    ResolutionResult,
)
from acios_discovery.domain.discovery.company_match_repository import (
    CompanyMatchRepository,
)
from acios_discovery.domain.discovery.models import (
    RawDiscovery,
)


class EntityResolutionService:

    def __init__(
        self,
        repository: CompanyMatchRepository,
        engine: EntityResolutionEngine,
    ) -> None:

        self._repository = repository

        self._engine = engine

    async def resolve(
        self,
        discovery: RawDiscovery,
    ) -> ResolutionResult:

        companies = await self._repository.candidates(
            discovery,
        )

        best_company = None
        best_score = 0.0

        for company in companies:

            score = self._engine.confidence(
                discovery,
                company,
            )

            if score > best_score:
                best_score = score
                best_company = company

        if best_company is None:
            return ResolutionResult(
                company=None,
                confidence=0.0,
                match=EntityMatch.DIFFERENT,
            )

        if best_score >= 80.0:
            match = EntityMatch.STRONG_MATCH

        elif best_score >= 60.0:
            match = EntityMatch.POSSIBLE_MATCH

        else:
            match = EntityMatch.DIFFERENT

        return ResolutionResult(
            company=best_company,
            confidence=best_score,
            match=match,
        )
