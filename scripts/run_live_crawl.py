from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import time
from contextlib import contextmanager

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
)
from acios_discovery.application.planning.crawl_plan_generator import (
    CrawlPlanGenerator,
)
from acios_discovery.application.planning.filtered_crawl_plan_generator import (
    FilteredCrawlPlanGenerator,
)
from acios_discovery.application.planning.models import CrawlPlan
from acios_discovery.application.planning.providers.category_provider import (
    CategoryProvider,
)
from acios_discovery.application.planning.providers.city_provider import (
    CityProvider,
)
from acios_discovery.application.proxy import AdaptiveProxyPool
from acios_discovery.application.subscribers.progress_bar_subscriber import (
    ProgressBarSubscriber,
)
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

STALL_THRESHOLD_SECONDS = 30
HEARTBEAT_INTERVAL_SECONDS = 1


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


@contextmanager
def _limit_logging_to_warnings():
    """
    Raises the root logger's level to WARNING for the duration
    of the block, restoring the previous level afterward (even
    on exception).

    This hides routine INFO-level noise (HTTP requests, merge
    details) from the terminal so the progress bar stays clean,
    while WARNING/ERROR — proxy backoff, job failures, fallback-
    page detections — still print. A crawl that hangs or fails
    therefore remains diagnosable from the terminal alone,
    instead of showing nothing but a frozen progress bar.
    """

    root = logging.getLogger()

    previous_level = root.level

    root.setLevel(logging.WARNING)

    try:
        yield
    finally:
        root.setLevel(previous_level)


async def _heartbeat(
    *,
    progress: Progress,
    task_id,
    subscriber: ProgressBarSubscriber,
    state: str,
) -> None:
    """
    Updates the progress bar's description to surface a stall —
    no job has completed or failed for STALL_THRESHOLD_SECONDS —
    so a genuinely hung crawl is visible as more than a static
    percentage. Cancelled when the crawl finishes.
    """

    base_description = f"Crawling {state}..."

    try:
        while True:
            await asyncio.sleep(HEARTBEAT_INTERVAL_SECONDS)

            idle_seconds = (
                time.monotonic() - subscriber.last_event_at
            )

            if idle_seconds >= STALL_THRESHOLD_SECONDS:
                progress.update(
                    task_id,
                    description=(
                        f"{base_description} "
                        f"(no progress for {int(idle_seconds)}s — "
                        f"still working, likely a slow proxy)"
                    ),
                )
            else:
                progress.update(
                    task_id,
                    description=base_description,
                )

    except asyncio.CancelledError:
        pass


async def _build_http_client(
    metrics: CrawlMetricsService,
) -> HttpClient:
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
        metrics=metrics,
    )


async def main() -> None:

    parser = argparse.ArgumentParser(
        description="Run a live, bounded discovery crawl against "
        "the real database and Finelib.",
    )
    parser.add_argument(
        "--resume",
        dest="resume_session_id",
        default=None,
        help="Session id to resume from a previous run's checkpoint. "
        "--state (and --category, if the original run used one) "
        "must be supplied again and match the original run — "
        "resume does not currently remember them automatically.",
    )
    parser.add_argument(
        "--state",
        required=True,
        help="Nigerian state to crawl. Required — there is no "
        "default, so a run always crawls exactly the state you "
        "asked for.",
    )
    parser.add_argument(
        "--category",
        dest="categories",
        action="append",
        default=None,
        help="Limit to this category slug. Repeatable "
        "(e.g. --category healthcare --category restaurants). "
        "Omit to crawl every registered category.",
    )
    parser.add_argument(
        "--max-jobs",
        type=int,
        default=None,
        help="Cap the number of (city, category) jobs submitted "
        "in this run. Omit for no cap.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate and print the plan count without "
        "submitting any jobs or making any network requests.",
    )
    parser.add_argument(
        "--two-plan",
        action="store_true",
        help="Use the original bounded two-plan demo generator "
        "(Lagos + Ikeja healthcare only) instead of the full "
        "state-level generator. For quick smoke tests.",
    )
    args = parser.parse_args()

    if args.two_plan:
        planner = TwoPlanGenerator()
    else:
        planner = FilteredCrawlPlanGenerator(
            inner=CrawlPlanGenerator(
                city_provider=CityProvider(),
                category_provider=CategoryProvider(),
            ),
            categories=args.categories,
            max_jobs=args.max_jobs,
        )

    if args.dry_run:
        plans = planner.generate(state=args.state)
        print()
        print("=" * 80)
        print("DRY RUN")
        print("=" * 80)
        print(f"State                : {args.state}")
        print(f"Categories filter    : {args.categories or 'all'}")
        print(f"Max jobs cap         : {args.max_jobs or 'none'}")
        print(f"Plans that would run : {len(plans)}")
        print("=" * 80)
        by_city: dict[str, int] = {}
        for plan in plans:
            by_city[plan.city] = by_city.get(plan.city, 0) + 1
        for city, count in sorted(by_city.items()):
            print(f"  {city}: {count} jobs")
        return

    console = Console()

    configure_logging(console=console)

    if args.resume_session_id is not None:
        console.print(
            "[yellow]Resuming session — make sure --state"
            + (" and --category" if args.categories else "")
            + f" match the original run exactly. Resuming as: "
            f"state={args.state!r}, categories="
            f"{args.categories or 'all'}[/yellow]"
        )

    metrics = CrawlMetricsService()

    http = await _build_http_client(metrics)

    # Job count is known upfront for a fresh run (same plans the
    # execution service will independently generate). On resume,
    # the real count depends on DB-side filtering that only
    # happens inside execution_service.run(), so an indeterminate
    # spinner is used instead of a determinate bar.
    is_resume = args.resume_session_id is not None

    expected_job_count = (
        None
        if is_resume
        else len(planner.generate(state=args.state))
    )

    async with SessionFactory() as session:

        services = DiscoveryServices(
            session=session,
            workers=1,
            http=http,
            planner=planner,
            resume_session_id=args.resume_session_id,
            metrics=metrics,
        )

        session_id = services.crawling.session.id

        console.print()
        console.print("=" * 80)
        console.print(f"Session ID: {session_id}")
        console.print("=" * 80)
        console.print(
            "Copy this session ID — you'll need it to test resume "
            "if you interrupt this run (Ctrl+C)."
        )
        console.print()

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        )

        heartbeat_task: asyncio.Task | None = None

        try:
            with progress:

                task_id = progress.add_task(
                    f"Crawling {args.state}...",
                    total=expected_job_count,
                )

                progress_subscriber = ProgressBarSubscriber(
                    progress=progress,
                    task_id=task_id,
                )

                services.crawling.publisher.subscribe(
                    progress_subscriber,
                )

                heartbeat_task = asyncio.create_task(
                    _heartbeat(
                        progress=progress,
                        task_id=task_id,
                        subscriber=progress_subscriber,
                        state=args.state,
                    )
                )

                with _limit_logging_to_warnings():

                    result = await services.execution_service.run(
                        state=args.state,
                    )

        except (KeyboardInterrupt, asyncio.CancelledError):

            console.print()
            console.print(
                "[bold yellow]Interrupted.[/bold yellow] "
                "Session progress up to this point is saved."
            )
            console.print(
                f"Resume with: [bold]--resume {session_id} "
                f"--state {args.state}"
                + (
                    " ".join(
                        f" --category {c}"
                        for c in (args.categories or [])
                    )
                )
                + "[/bold]"
            )
            sys.exit(130)

        finally:
            if heartbeat_task is not None:
                heartbeat_task.cancel()

        await session.commit()

        console.print()
        console.print("=" * 80)
        console.print("EXECUTION RESULT")
        console.print("=" * 80)
        console.print(f"Session ID           : {result.session_id}")
        console.print(f"Resumed              : {result.resumed}")
        console.print(f"Plans generated      : {result.plans_generated}")
        console.print(f"Jobs submitted       : {result.jobs_submitted}")
        console.print(f"Jobs processed       : {result.jobs_processed}")
        console.print(f"Pages crawled        : {result.pages_crawled}")
        console.print(
            f"Companies discovered : {result.companies_discovered}"
        )
        console.print(
            f"Enrichment failures  : {result.enrichment_failures}"
        )
        console.print(f"Workers              : {result.workers}")
        console.print("=" * 80)

        metrics_snapshot = services.crawling.metrics.snapshot()

        console.print()
        console.print("=" * 80)
        console.print("METRICS SNAPSHOT")
        console.print("=" * 80)
        console.print(
            f"HTTP requests sent   : {metrics_snapshot.requests_sent}"
        )
        console.print(
            f"HTTP successes       : "
            f"{metrics_snapshot.successful_requests}"
        )
        console.print(
            f"HTTP failures        : {metrics_snapshot.http_failures}"
        )
        console.print(
            f"Duplicates merged    : {metrics_snapshot.duplicates_found}"
        )
        console.print(
            f"Proxy retries        : {metrics_snapshot.proxy_retries}"
        )
        console.print(f"Job retries          : {metrics_snapshot.retries}")
        console.print(f"Job failures         : {metrics_snapshot.failures}")
        console.print(
            f"Duration (s)         : "
            f"{metrics_snapshot.duration_seconds:.2f}"
        )
        console.print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Reached only if the interrupt lands outside main()'s
        # own try block (e.g. during asyncio shutdown/cleanup
        # after main() has already returned or re-raised). The
        # in-run interrupt message is printed inside main(); this
        # is a silent, clean exit for whatever slips past it.
        sys.exit(130)
