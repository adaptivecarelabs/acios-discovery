from __future__ import annotations

from acios_discovery.application.discovery.discovery_execution_result import (
    DiscoveryExecutionResult,
)
from acios_discovery.application.discovery.discovery_execution_service import (
    DiscoveryExecutionService,
)
from acios_discovery.infrastructure.persistence.session import (
    session_scope,
)

from .discovery_services import DiscoveryServices


async def run_discovery(
    *,
    state: str,
    workers: int = 4,
) -> DiscoveryExecutionResult:
    """
    Execute one complete discovery operation.

    The execution service owns planning, job submission,
    crawl supervision, and result aggregation.

    One database session is shared by the discovery subsystem.
    """

    async with session_scope() as session:
        services = DiscoveryServices(
            session=session,
            workers=workers,
        )

        execution_service: DiscoveryExecutionService = (
            services.execution_service
        )

        return await execution_service.run(
            state=state,
        )
