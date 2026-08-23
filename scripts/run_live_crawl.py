from __future__ import annotations

import argparse
import asyncio

from acios_discovery.application.planning.models import CrawlPlan
from acios_discovery.application.proxy import AdaptiveProxyPool
from acios_discovery.bootstrap.discovery_services import DiscoveryServices
from acios_discovery.domain.http import HttpClient
from acios_discovery.infrastructure.http.httpx_client import HttpxClient
from acios_discovery.infrastructure.http.proxy_rotating_http_client import (
    ProxyRotatingHttpClient,
)
from acios_discovery.infrastructure.persistence.config import WEBSHARE_API_KEY
from acios_discovery.infrastructure.persistence.database import SessionFactory
from acios_discovery.infrastructure.proxy import WebshareProxyProvider
from acios_discovery.shared.logging import configure_logging, logger


class TwoPlanGenerator:
    """
    Deliberately bounded planner for live validation runs — two
    (city, category) pairs, not a full state.
    """

    def generate(self, *, state: str) -> list[CrawlPlan]:
        return [
            CrawlPlan(state=state, city="Lagos", category_slug="healthcare"),
            CrawlPlan(state=state, city="Ikeja", category_slug="healthcare"),
        ]


async def _build_http_client() -> HttpClient:
    """
    Builds a proxy-rotating HTTP client if WEBSHARE_API_KEY is
    configured, falling back to a plain direct-connection client
    otherwise. Proxy rotation is therefore opt-in: the crawler
    still runs correctly with no proxy setup at all.
    """

    if not WEBSHARE_API_KEY:
        logger.info(
            "WEBSHARE_API_KEY not set — crawling without proxy "
            "rotation.",
        )
        return HttpxClient()

    provider = WebshareProxyProvider(api_key=WEBSHARE_API_KEY)

    proxies = await provider.list_proxies()

    if not proxies:
        logger.warning(
            "WEBSHARE_API_KEY is set but no proxies were "
            "returned — crawling without proxy rotation.",
        )
        return HttpxClient()

    pool = AdaptiveProxyPool(proxies)

    logger.info(
        "Crawling through %d rotating proxies.",
        len(proxies),
    )

    return ProxyRotatingHttpClient(
        inner=HttpxClient(),
        pool=pool,
    )


async def main() -> None:

    configure_logging()

    parser = argparse.ArgumentParser(
        description="Run a live, bounded discovery crawl against "
        "the real database and Finelib.",
    )
    parser.add_argument(
        "--resume",
        dest="resume_session_id",
        default=None,
        help="Session id to resume from a previous run's checkpoint.",
    )
    args = parser.parse_args()

    http = await _build_http_client()

    async with SessionFactory() as session:

        services = DiscoveryServices(
            session=session,
            workers=1,
            http=http,
            planner=TwoPlanGenerator(),
            resume_session_id=args.resume_session_id,
        )

        print()
        print("=" * 80)
        print(f"Session ID: {services.crawling.session.id}")
        print("=" * 80)
        print(
            "Copy this session ID — you'll need it to test resume "
            "if you interrupt this run (Ctrl+C)."
        )
        print()

        result = await services.execution_service.run(state="Lagos")

        await session.commit()

        print()
        print("=" * 80)
        print("EXECUTION RESULT")
        print("=" * 80)
        print(f"Session ID           : {result.session_id}")
        print(f"Resumed              : {result.resumed}")
        print(f"Plans generated      : {result.plans_generated}")
        print(f"Jobs submitted       : {result.jobs_submitted}")
        print(f"Jobs processed       : {result.jobs_processed}")
        print(f"Pages crawled        : {result.pages_crawled}")
        print(f"Companies discovered : {result.companies_discovered}")
        print(f"Workers              : {result.workers}")
        print("=" * 80)

        metrics = services.crawling.metrics.snapshot()

        print()
        print("=" * 80)
        print("METRICS SNAPSHOT")
        print("=" * 80)
        print(f"HTTP requests sent   : {metrics.requests_sent}")
        print(f"HTTP successes       : {metrics.successful_requests}")
        print(f"HTTP failures        : {metrics.http_failures}")
        print(f"Job retries          : {metrics.retries}")
        print(f"Job failures         : {metrics.failures}")
        print(f"Duration (s)         : {metrics.duration_seconds:.2f}")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
