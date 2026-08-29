from __future__ import annotations

import time

import pytest

from acios_discovery.application.auth import (
    InvalidTokenError,
    TokenService,
)
from acios_discovery.domain.user import UserId, UserRole


def make_service(**kwargs) -> TokenService:
    return TokenService(secret_key="test-secret-key", **kwargs)


def test_create_and_verify_round_trip():
    service = make_service()

    token = service.create_access_token(
        user_id=UserId.from_sequence(1),
        role=UserRole.ADMIN,
    )

    payload = service.verify_access_token(token)

    assert payload.user_id == UserId.from_sequence(1)
    assert payload.role == UserRole.ADMIN


def test_verify_rejects_a_token_signed_with_a_different_secret():
    service_a = make_service()
    service_b = TokenService(secret_key="a-completely-different-secret")

    token = service_a.create_access_token(
        user_id=UserId.from_sequence(1),
        role=UserRole.MEMBER,
    )

    with pytest.raises(InvalidTokenError):
        service_b.verify_access_token(token)


def test_verify_rejects_garbage_input():
    service = make_service()

    with pytest.raises(InvalidTokenError):
        service.verify_access_token("not-a-real-token")


def test_verify_rejects_an_expired_token():
    # expiry_minutes is a float in practice via timedelta, but
    # the constructor only accepts int minutes — use a fractional
    # workaround by monkeypatching isn't necessary: we can create
    # a token, then wait past a very short expiry.
    service = make_service(expiry_minutes=0)

    token = service.create_access_token(
        user_id=UserId.from_sequence(1),
        role=UserRole.MEMBER,
    )

    time.sleep(1.5)

    with pytest.raises(InvalidTokenError):
        service.verify_access_token(token)


def test_verify_rejects_a_token_with_an_unknown_role_value():
    """
    If a token's role claim doesn't match any current UserRole
    value (e.g. an old token signed before a role was renamed or
    removed), verification must fail closed, not default to some
    role.
    """

    import jose.jwt as jose_jwt

    service = make_service()

    bad_payload = {
        "sub": UserId.from_sequence(1).value,
        "role": "superuser",  # not a real UserRole value
    }

    bad_token = jose_jwt.encode(
        bad_payload,
        "test-secret-key",
        algorithm="HS256",
    )

    with pytest.raises(InvalidTokenError):
        service.verify_access_token(bad_token)
