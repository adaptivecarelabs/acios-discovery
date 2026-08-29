from __future__ import annotations

import asyncio

import pytest
from httpx import AsyncClient


async def _start_crawl(
    client: AsyncClient,
    token: str,
    *,
    state: str = "TestState",
    categories: list[str] | None = None,
    max_jobs: int | None = 2,
) -> dict:

    response = await client.post(
        "/crawl-sessions",
        json={
            "state": state,
            "categories": categories or ["test-category"],
            "max_jobs": max_jobs,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 202

    return response.json()


@pytest.mark.asyncio
async def test_starting_a_crawl_requires_authentication(
    api_client_with_fake_crawls: AsyncClient,
) -> None:

    response = await api_client_with_fake_crawls.post(
        "/crawl-sessions",
        json={"state": "TestState"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_starting_a_crawl_returns_the_stored_scope(
    api_client_with_slow_fake_crawls,
    admin_user,
    admin_token: str,
) -> None:
    """
    Uses the slow fake so the crawl is still genuinely in flight
    when we check the response — with the fast fake, the crawl
    can complete before this assertion runs, making the
    "pending" status flaky (it would sometimes legitimately have
    already flipped to "completed").
    """

    client, release_event = api_client_with_slow_fake_crawls

    try:
        body = await _start_crawl(
            client,
            admin_token,
            state="Rivers",
            categories=["construction"],
            max_jobs=5,
        )

        assert body["state"] == "Rivers"
        assert body["categories"] == ["construction"]
        assert body["max_jobs"] == 5
        assert body["triggered_by_user_id"] == "ACL-USR-00000001"
        assert body["status"] == "pending"

    finally:
        release_event.set()


@pytest.mark.asyncio
async def test_started_crawl_eventually_completes_and_is_listed(
    api_client_with_fake_crawls: AsyncClient,
    admin_user,
    admin_token: str,
) -> None:

    started = await _start_crawl(api_client_with_fake_crawls, admin_token)

    session_id = started["id"]

    # The fake crawl completes almost instantly, but it's still
    # a background task — poll briefly rather than assuming it's
    # already done the moment start() returns.
    for _ in range(20):
        response = await api_client_with_fake_crawls.get(
            f"/crawl-sessions/{session_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200

        if response.json()["status"] == "completed":
            break

        await asyncio.sleep(0.1)

    body = response.json()

    assert body["status"] == "completed"
    assert body["jobs_completed"] == 2
    assert body["companies_discovered"] == 6  # 2 jobs * 3 companies each


@pytest.mark.asyncio
async def test_getting_an_unknown_session_returns_404(
    api_client_with_fake_crawls: AsyncClient,
    admin_user,
    admin_token: str,
) -> None:

    response = await api_client_with_fake_crawls.get(
        "/crawl-sessions/does-not-exist",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_sessions_includes_a_started_session(
    api_client_with_fake_crawls: AsyncClient,
    admin_user,
    admin_token: str,
) -> None:

    started = await _start_crawl(api_client_with_fake_crawls, admin_token)

    response = await api_client_with_fake_crawls.get(
        "/crawl-sessions",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200

    ids = {s["id"] for s in response.json()}

    assert started["id"] in ids


@pytest.mark.asyncio
async def test_non_admin_member_can_still_start_and_view_crawls(
    api_client_with_fake_crawls: AsyncClient,
    admin_user,
    admin_token: str,
) -> None:
    """
    Crawl-session endpoints are intentionally NOT admin-only —
    any authenticated user can trigger and monitor crawls; only
    user management is admin-restricted.
    """

    create_response = await api_client_with_fake_crawls.post(
        "/users",
        json={
            "email": "member@example.com",
            "password": "member-password-123",
            "role": "member",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert create_response.status_code == 201

    login_response = await api_client_with_fake_crawls.post(
        "/auth/login",
        data={
            "username": "member@example.com",
            "password": "member-password-123",
        },
    )
    member_token = login_response.json()["access_token"]

    body = await _start_crawl(
        api_client_with_fake_crawls,
        member_token,
    )

    assert body["triggered_by_user_id"] == "ACL-USR-00000002"

    list_response = await api_client_with_fake_crawls.get(
        "/crawl-sessions",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert list_response.status_code == 200


@pytest.mark.asyncio
async def test_resuming_a_completed_session_uses_stored_scope(
    api_client_with_fake_crawls: AsyncClient,
    admin_user,
    admin_token: str,
) -> None:

    started = await _start_crawl(
        api_client_with_fake_crawls,
        admin_token,
        state="Ogun",
        categories=["retail"],
        max_jobs=1,
    )

    session_id = started["id"]

    # Wait for the original run to finish before resuming.
    for _ in range(20):
        status_response = await api_client_with_fake_crawls.get(
            f"/crawl-sessions/{session_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        if status_response.json()["status"] == "completed":
            break
        await asyncio.sleep(0.1)

    resume_response = await api_client_with_fake_crawls.post(
        f"/crawl-sessions/{session_id}/resume",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert resume_response.status_code == 202

    body = resume_response.json()

    # Resume must reflect the ORIGINAL scope, without the caller
    # having re-supplied it — this is the whole point of storing
    # scope on the session.
    assert body["state"] == "Ogun"
    assert body["categories"] == ["retail"]


@pytest.mark.asyncio
async def test_resuming_an_unknown_session_returns_400(
    api_client_with_fake_crawls: AsyncClient,
    admin_user,
    admin_token: str,
) -> None:

    response = await api_client_with_fake_crawls.post(
        "/crawl-sessions/does-not-exist/resume",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_events_stream_returns_404_for_a_non_running_session(
    api_client_with_fake_crawls: AsyncClient,
    admin_user,
    admin_token: str,
) -> None:

    response = await api_client_with_fake_crawls.get(
        "/crawl-sessions/does-not-exist/events",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_starting_a_second_crawl_with_the_same_scope_is_rejected(
    api_client_with_slow_fake_crawls,
    admin_user,
    admin_token: str,
) -> None:
    """
    Two overlapping crawls for the same (state, categories)
    scope must not both be allowed to run concurrently — this
    would waste proxy budget and race each other's writes.
    """

    client, release_event = api_client_with_slow_fake_crawls

    try:
        first = await _start_crawl(
            client,
            admin_token,
            state="Kano",
            categories=["retail"],
        )

        response = await client.post(
            "/crawl-sessions",
            json={
                "state": "Kano",
                "categories": ["retail"],
                "max_jobs": 2,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 409
        assert first["id"] is not None  # sanity: first genuinely started

    finally:
        release_event.set()


@pytest.mark.asyncio
async def test_category_order_does_not_bypass_collision_protection(
    api_client_with_slow_fake_crawls,
    admin_user,
    admin_token: str,
) -> None:
    """
    ["a", "b"] and ["b", "a"] describe the same scope and must
    be recognized as colliding, not treated as different crawls.
    """

    client, release_event = api_client_with_slow_fake_crawls

    try:
        await _start_crawl(
            client,
            admin_token,
            state="Kano",
            categories=["retail", "construction"],
        )

        response = await client.post(
            "/crawl-sessions",
            json={
                "state": "Kano",
                "categories": ["construction", "retail"],
                "max_jobs": 2,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 409

    finally:
        release_event.set()


@pytest.mark.asyncio
async def test_different_scope_crawls_can_run_concurrently(
    api_client_with_slow_fake_crawls,
    admin_user,
    admin_token: str,
) -> None:
    """
    Collision protection must only block genuinely overlapping
    scope — different states, or different categories within
    the same state, are legitimately independent and must both
    be allowed to start.
    """

    client, release_event = api_client_with_slow_fake_crawls

    try:
        first = await _start_crawl(
            client,
            admin_token,
            state="Kano",
            categories=["retail"],
        )

        second_response = await client.post(
            "/crawl-sessions",
            json={
                "state": "Kano",
                "categories": ["construction"],  # different category
                "max_jobs": 2,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert second_response.status_code == 202

        third_response = await client.post(
            "/crawl-sessions",
            json={
                "state": "Ogun",  # different state, same category
                "categories": ["retail"],
                "max_jobs": 2,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert third_response.status_code == 202

    finally:
        release_event.set()


@pytest.mark.asyncio
async def test_resuming_a_session_that_is_currently_running_is_rejected(
    api_client_with_slow_fake_crawls,
    admin_user,
    admin_token: str,
) -> None:

    client, release_event = api_client_with_slow_fake_crawls

    try:
        started = await _start_crawl(client, admin_token)

        response = await client.post(
            f"/crawl-sessions/{started['id']}/resume",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 409

    finally:
        release_event.set()
