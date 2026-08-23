from __future__ import annotations

from dataclasses import dataclass, field

from acios_discovery.domain.proxy import Proxy


@dataclass(slots=True)
class ProxyState:
    """
    Mutable adaptive rate-limiting state for one proxy.

    next_available_at and current_delay use asyncio's monotonic
    event-loop clock (time.monotonic()), not wall-clock time.
    """

    proxy: Proxy

    current_delay: float

    next_available_at: float = field(default=0.0)

    consecutive_failures: int = field(default=0)
