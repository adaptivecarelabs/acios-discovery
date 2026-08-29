from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_openapi_schema_is_reachable(api_client: AsyncClient) -> None:
    response = await api_client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Acios Discovery API"
