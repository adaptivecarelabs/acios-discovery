from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _create_member(
    api_client: AsyncClient,
    admin_token: str,
    email: str = "member@example.com",
) -> dict:

    response = await api_client.post(
        "/users",
        json={
            "email": email,
            "password": "member-password-123",
            "role": "member",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 201

    return response.json()


async def _login(
    api_client: AsyncClient,
    email: str,
    password: str,
) -> str:

    response = await api_client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_admin_can_create_a_user(
    api_client: AsyncClient,
    admin_user,
    admin_token: str,
) -> None:

    body = await _create_member(api_client, admin_token)

    assert body["email"] == "member@example.com"
    assert body["role"] == "member"
    assert body["active"] is True


@pytest.mark.asyncio
async def test_creating_a_duplicate_email_fails(
    api_client: AsyncClient,
    admin_user,
    admin_token: str,
) -> None:

    await _create_member(api_client, admin_token)

    response = await api_client.post(
        "/users",
        json={
            "email": "member@example.com",
            "password": "another-password",
            "role": "member",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_creating_a_user_with_an_invalid_role_fails(
    api_client: AsyncClient,
    admin_user,
    admin_token: str,
) -> None:

    response = await api_client.post(
        "/users",
        json={
            "email": "someone@example.com",
            "password": "password123",
            "role": "superuser",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_non_admin_cannot_create_a_user(
    api_client: AsyncClient,
    admin_user,
    admin_token: str,
) -> None:

    await _create_member(api_client, admin_token)

    member_token = await _login(
        api_client,
        "member@example.com",
        "member-password-123",
    )

    response = await api_client.post(
        "/users",
        json={
            "email": "another@example.com",
            "password": "password123",
            "role": "member",
        },
        headers={"Authorization": f"Bearer {member_token}"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_non_admin_cannot_list_users(
    api_client: AsyncClient,
    admin_user,
    admin_token: str,
) -> None:

    await _create_member(api_client, admin_token)

    member_token = await _login(
        api_client,
        "member@example.com",
        "member-password-123",
    )

    response = await api_client.get(
        "/users",
        headers={"Authorization": f"Bearer {member_token}"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_list_users(
    api_client: AsyncClient,
    admin_user,
    admin_token: str,
) -> None:

    await _create_member(api_client, admin_token)

    response = await api_client.get(
        "/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200

    emails = {u["email"] for u in response.json()}

    assert "admin@example.com" in emails
    assert "member@example.com" in emails


@pytest.mark.asyncio
async def test_admin_can_deactivate_a_user(
    api_client: AsyncClient,
    admin_user,
    admin_token: str,
) -> None:

    member = await _create_member(api_client, admin_token)

    response = await api_client.patch(
        f"/users/{member['id']}",
        json={"active": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.json()["active"] is False


@pytest.mark.asyncio
async def test_deactivated_user_cannot_log_in(
    api_client: AsyncClient,
    admin_user,
    admin_token: str,
) -> None:

    member = await _create_member(api_client, admin_token)

    await api_client.patch(
        f"/users/{member['id']}",
        json={"active": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    response = await api_client.post(
        "/auth/login",
        data={
            "username": "member@example.com",
            "password": "member-password-123",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_existing_token_stops_working_after_deactivation(
    api_client: AsyncClient,
    admin_user,
    admin_token: str,
) -> None:

    member = await _create_member(api_client, admin_token)

    member_token = await _login(
        api_client,
        "member@example.com",
        "member-password-123",
    )

    # Token works before deactivation.
    ok_response = await api_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert ok_response.status_code == 200

    await api_client.patch(
        f"/users/{member['id']}",
        json={"active": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Same, still-unexpired token now rejected.
    response = await api_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {member_token}"},
    )

    assert response.status_code == 401
