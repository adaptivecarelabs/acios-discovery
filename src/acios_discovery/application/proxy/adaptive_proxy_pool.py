from __future__ import annotations

import asyncio
import time

from acios_discovery.domain.proxy import Proxy
from acios_discovery.shared.logging import logger

from .proxy_state import ProxyState


class AdaptiveProxyPool:
    """
    Selects a proxy for each outgoing request and adapts each
    proxy's individual delay based on how that specific proxy
    has been treated by the target site.

    Each proxy tracks its own next_available_at. acquire()
    always returns the proxy that becomes available soonest,
    waiting if none are currently available. This means a proxy
    that just got a 429 backs off on its own without slowing
    down every other proxy in the pool.

    Not thread-safe across processes; safe for concurrent
    asyncio tasks within one process via the internal lock.
    """

    def __init__(
        self,
        proxies: list[Proxy],
        *,
        min_delay: float = 2.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        recovery_multiplier: float = 0.9,
    ) -> None:

        if not proxies:
            raise ValueError(
                "AdaptiveProxyPool requires at least one proxy",
            )

        self._min_delay = min_delay
        self._max_delay = max_delay
        self._backoff_multiplier = backoff_multiplier
        self._recovery_multiplier = recovery_multiplier

        self._states: dict[Proxy, ProxyState] = {
            proxy: ProxyState(
                proxy=proxy,
                current_delay=min_delay,
                next_available_at=0.0,
            )
            for proxy in proxies
        }

        self._lock = asyncio.Lock()

    async def acquire(self) -> ProxyState:
        """
        Return the proxy that becomes available soonest,
        blocking until it actually is.

        Reserves that proxy's next slot optimistically (sets
        next_available_at forward by current_delay) before
        returning, so concurrent callers don't pick the same
        proxy for overlapping requests.
        """

        async with self._lock:

            state = min(
                self._states.values(),
                key=lambda s: s.next_available_at,
            )

            now = time.monotonic()

            wait_time = max(
                0.0,
                state.next_available_at - now,
            )

            # Reserve this proxy's next slot now, while holding
            # the lock, so a second concurrent acquire() doesn't
            # also select this proxy before we've released it.
            state.next_available_at = (
                max(now, state.next_available_at)
                + state.current_delay
            )

        if wait_time > 0:
            await asyncio.sleep(wait_time)

        return state

    def report_success(
        self,
        state: ProxyState,
    ) -> None:

        state.current_delay = max(
            self._min_delay,
            state.current_delay * self._recovery_multiplier,
        )

        state.consecutive_failures = 0

    def report_failure(
        self,
        state: ProxyState,
        *,
        retryable: bool,
    ) -> None:

        state.consecutive_failures += 1

        if not retryable:
            return

        old_delay = state.current_delay

        state.current_delay = min(
            self._max_delay,
            state.current_delay * self._backoff_multiplier,
        )

        logger.warning(
            "Backing off proxy %s: %.1fs -> %.1fs "
            "(%d consecutive failures)",
            state.proxy,
            old_delay,
            state.current_delay,
            state.consecutive_failures,
        )

    def snapshot(self) -> list[ProxyState]:
        """
        Read-only view of current per-proxy state, for metrics
        or debugging.
        """
        return list(self._states.values())
