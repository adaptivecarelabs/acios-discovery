from __future__ import annotations

from abc import ABC, abstractmethod

from .proxy import Proxy


class ProxyProvider(ABC):
    """
    Supplies the pool of proxies available for crawling.
    """

    @abstractmethod
    async def list_proxies(self) -> list[Proxy]:
        ...
