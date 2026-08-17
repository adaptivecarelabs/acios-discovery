from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.bootstrap.discovery_services import (
    DiscoveryServices,
)


@pytest.mark.asyncio
async def test_discovery_services_exposes_execution_service() -> None:
    session = MagicMock(
        spec=AsyncSession,
    )

    services = DiscoveryServices(
        session=session,
        workers=4,
    )

    assert services.execution_service is not None
