from __future__ import annotations

from acios_discovery.application.resolution.entity_resolution_engine import (
    EntityResolutionEngine,
)
from acios_discovery.application.resolution.resolution_result import (
    ResolutionResult,
)
from acios_discovery.domain.company.company_repository import (
    CompanyRepository,
)
from acios_discovery.domain.discovery.models import (
    RawDiscovery,
)


class EntityResolutionService:

    def __init__(
        self,
        repository: CompanyRepository,
        engine: EntityResolutionEngine,
    ) -> None:

        self._repository = repository

        self._engine = engine

    async def resolve(
        self,
        discovery: RawDiscovery,
    ) -> ResolutionResult:

        companies = await self._repository.list_all()

        best_company = None

        best_score = 0.0

        for company in companies:

            score = self._engine.confidence(
                discovery,
                company,
            )

            print(
                f"{discovery.business_name:<45}"
                f" -> "
                f"{company.canonical_name:<45}"
                f" = {score:.2f}"
            )

            if score > best_score:

                best_score = score

                best_company = company

        duplicate = best_score >= 80.0            

        return ResolutionResult(
            company=best_company,
            confidence=best_score,
            duplicate=duplicate,
        )
