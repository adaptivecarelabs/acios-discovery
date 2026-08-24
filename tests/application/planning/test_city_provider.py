from acios_discovery.application.planning.providers.city_provider import (
    CityProvider,
)


def test_returns_lagos_cities():

    provider = CityProvider()

    cities = provider.get_cities(
        "Lagos",
    )

    assert "Ikeja" in cities

    assert "Badagry" in cities


def test_unknown_state_returns_empty():

    provider = CityProvider()

    assert (
        provider.get_cities(
            "Atlantis",
        )
        == []
    )
