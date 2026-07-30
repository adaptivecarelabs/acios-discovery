from __future__ import annotations

from acios_discovery.domain.discovery.models import RawDiscovery


class FinelibParser:
    """
    Parses Finelib directory pages.
    """

    def parse(self, html: str) -> list[RawDiscovery]:
        raise NotImplementedError
