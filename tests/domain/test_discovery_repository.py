from inspect import isabstract

from acios_discovery.domain.repositories.discovery import (
    DiscoveryRepository,
)


def test_repository_is_abstract() -> None:
    assert isabstract(DiscoveryRepository)
