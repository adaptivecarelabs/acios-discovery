from acios_discovery.application.planning.providers.state_provider import (
    StateProvider,
)


def test_returns_states():

    provider = StateProvider()

    states = provider.get_states()

    assert "Lagos" in states

    assert len(states) == 37
