from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_succeeds_with_correct_credentials(
    api_client: AsyncClient,
    admin_user,
) -> None:

    response = await api_client.post(
        "/auth/login",
        data={
            "username": "admin@example.com",
            "password": "admin-password-123",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["token_type"] == "bearer"
    assert body["access_token"]


@pytest.mark.asyncio
async def test_login_fails_with_wrong_password(
    api_client: AsyncClient,
    admin_user,
) -> None:

    response = await api_client.post(
        "/auth/login",
        data={
            "username": "admin@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_fails_for_unknown_email(
    api_client: AsyncClient,
) -> None:

    response = await api_client.post(
        "/auth/login",
        data={
            "username": "nobody@example.com",
            "password": "anything",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_authentication(
    api_client: AsyncClient,
) -> None:

    response = await api_client.get("/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_current_user_with_valid_token(
    api_client: AsyncClient,
    admin_user,
    admin_token: str,
) -> None:

    response = await api_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["email"] == "admin@example.com"
    assert body["role"] == "admin"


@pytest.mark.asyncio
async def test_me_rejects_a_garbage_token(
    api_client: AsyncClient,
) -> None:

    response = await api_client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401
