from __future__ import annotations

from abc import ABC, abstractmethod

from acios_discovery.domain.discovery.models import RawDiscovery


class BaseDirectoryParser(ABC):
    """Base contract for all directory parsers."""

    @abstractmethod
    def parse(self, html: str) -> list[RawDiscovery]:
        """Parse raw HTML into discovery objects."""
        raise NotImplementedError
