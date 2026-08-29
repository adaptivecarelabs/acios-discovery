import pytest

from acios_discovery.application.planning.providers.city_provider import (
    CityProvider,
    UnknownStateError,
)


def test_returns_lagos_cities():

    provider = CityProvider()

    cities = provider.get_cities(
        "Lagos",
    )

    assert "Ikeja" in cities

    assert "Badagry" in cities


def test_get_cities_is_case_insensitive():
    """
    Regression test: --state rivers / --state RIVERS / --state
    Rivers must all resolve to the same city list. Previously an
    exact-match lookup silently returned an empty list for any
    casing other than the one stored in nigeria_cities.json,
    producing a crawl with zero plans and no error.
    """

    provider = CityProvider()

    lowercase = provider.get_cities("rivers")
    exact_case = provider.get_cities("Rivers")
    uppercase = provider.get_cities("RIVERS")

    assert lowercase == exact_case == uppercase
    assert len(lowercase) > 0


def test_get_cities_ignores_surrounding_whitespace():

    provider = CityProvider()

    assert provider.get_cities(" Lagos ") == provider.get_cities("Lagos")


def test_unknown_state_raises_with_available_states_listed():

    provider = CityProvider()

    with pytest.raises(UnknownStateError) as exc_info:
        provider.get_cities("Atlantis")

    assert "Atlantis" in str(exc_info.value)
    assert "Lagos" in str(exc_info.value)


def test_canonical_state_name_returns_correct_casing():

    provider = CityProvider()

    assert provider.canonical_state_name("rivers") == "Rivers"
    assert provider.canonical_state_name("LAGOS") == "Lagos"


def test_canonical_state_name_raises_for_unknown_state():

    provider = CityProvider()

    with pytest.raises(UnknownStateError):
        provider.canonical_state_name("Atlantis")
