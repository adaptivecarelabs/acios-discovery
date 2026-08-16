from inspect import isabstract

from acios_discovery.domain.discovery.repository import (
    DiscoveryRepository,
)


def test_repository_is_abstract() -> None:
    assert isabstract(DiscoveryRepository)
