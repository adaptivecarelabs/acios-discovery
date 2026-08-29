from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
)
from acios_discovery.application.proxy import AdaptiveProxyPool
from acios_discovery.domain.errors.crawl_errors import (
    FatalCrawlError,
    RetryableCrawlError,
)
from acios_discovery.domain.http import HttpClient
from acios_discovery.infrastructure.http.httpx_client import HttpxClient
from acios_discovery.shared.logging import logger


class ProxyRotatingHttpClient(HttpClient):
    """
    Routes every request through the adaptive proxy pool.

    On a retryable failure (timeout, connection error, 429/5xx),
    that proxy's backoff grows and a different proxy is tried,
    up to max_attempts. A fatal (non-retryable) error is raised
    immediately without trying another proxy, since retrying a
    genuine 4xx (other than 429) on a different IP would not
    help and would just burn through the pool.
    """

    def __init__(
        self,
        *,
        inner: HttpxClient,
        pool: AdaptiveProxyPool,
        max_attempts: int = 3,
        metrics: CrawlMetricsService | None = None,
    ) -> None:
        self._inner = inner
        self._pool = pool
        self._max_attempts = max_attempts
        self._metrics = metrics

    async def get(
        self,
        url: str,
    ) -> str:

        last_exc: Exception | None = None

        for attempt in range(1, self._max_attempts + 1):

            state = await self._pool.acquire()

            try:
                result = await self._inner.get(
                    url,
                    proxy=state.proxy,
                )

            except RetryableCrawlError as exc:

                self._pool.report_failure(
                    state,
                    retryable=True,
                )

                if self._metrics is not None:
                    self._metrics.record_proxy_retry()

                last_exc = exc

                logger.warning(
                    "Retryable failure via proxy %s "
                    "(attempt %d/%d) for %s: %s",
                    state.proxy,
                    attempt,
                    self._max_attempts,
                    url,
                    exc,
                )

                continue
            except FatalCrawlError:

                self._pool.report_failure(
                    state,
                    retryable=False,
                )

                raise

            else:

                self._pool.report_success(state)

                return result

        assert last_exc is not None

        raise last_exc

    async def post_json(
        self,
        url: str,
        *,
        json: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> Any:

        last_exc: Exception | None = None

        for attempt in range(1, self._max_attempts + 1):

            state = await self._pool.acquire()

            try:
                result = await self._inner.post_json(
                    url,
                    json=json,
                    headers=headers,
                    proxy=state.proxy,
                )

            except RetryableCrawlError as exc:

                self._pool.report_failure(
                    state,
                    retryable=True,
                )

                if self._metrics is not None:
                    self._metrics.record_proxy_retry()

                last_exc = exc

                logger.warning(
                    "Retryable failure via proxy %s "
                    "(attempt %d/%d) posting to %s: %s",
                    state.proxy,
                    attempt,
                    self._max_attempts,
                    url,
                    exc,
                )

                continue
            except FatalCrawlError:

                self._pool.report_failure(
                    state,
                    retryable=False,
                )

                raise

            else:

                self._pool.report_success(state)

                return result

        assert last_exc is not None

        raise last_exc
