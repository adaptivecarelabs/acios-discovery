from __future__ import annotations

from acios_discovery.application.auth import hash_password, verify_password


def test_hash_password_produces_a_different_string_than_the_input():
    hashed = hash_password("my-secret-password")
    assert hashed != "my-secret-password"


def test_verify_password_accepts_the_correct_password():
    hashed = hash_password("correct-password")
    assert verify_password("correct-password", hashed) is True


def test_verify_password_rejects_the_wrong_password():
    hashed = hash_password("correct-password")
    assert verify_password("wrong-password", hashed) is False


def test_hashing_the_same_password_twice_produces_different_hashes():
    """
    bcrypt salts each hash independently — this guards against a
    regression to a non-salted or deterministic scheme, which
    would make identical passwords produce identical hashes and
    leak information via hash comparison.
    """
    first = hash_password("same-password")
    second = hash_password("same-password")
    assert first != second

    # Both still verify correctly despite being different strings.
    assert verify_password("same-password", first) is True
    assert verify_password("same-password", second) is True
