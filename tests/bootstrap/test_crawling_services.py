from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast
from unittest.mock import Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.application.discovery.pipeline import (
    DiscoveryPipeline,
)
from acios_discovery.application.planning.builders.listing_url_builder import (
    ListingUrlBuilder,
)
from acios_discovery.application.subscribers.crawl_metrics_subscriber import (
    CrawlMetricsSubscriber,
)
from acios_discovery.bootstrap.crawling_services import (
    CrawlingServices,
)
from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.events.page_crawled_event import (
    PageCrawledEvent,
)
from acios_discovery.domain.sources import Source


class FakeListingBuilder:
    pass


def make_pipeline_factory() -> Callable[
    [AsyncSession],
    DiscoveryPipeline,
]:
    return cast(
        Callable[
            [AsyncSession],
            DiscoveryPipeline,
        ],
        Mock(),
    )


def make_session_factory() -> Callable[
    [],
    Awaitable[AsyncSession],
]:
    return cast(
        Callable[
            [],
            Awaitable[AsyncSession],
        ],
        Mock(),
    )


def build_services() -> CrawlingServices:
    return CrawlingServices(
        pipeline_factory=make_pipeline_factory(),
        session_factory=make_session_factory(),
        listing_builder=cast(
            ListingUrlBuilder,
            FakeListingBuilder(),
        ),
        workers=4,
    )


def test_crawling_services_builds_execution_graph() -> None:
    services = build_services()

    assert services.queue is not None
    assert services.scheduler is not None
    assert services.job_factory is not None
    assert services.submission_service is not None
    assert services.metrics is not None
    assert services.publisher is not None
    assert services.worker_factory is not None
    assert services.worker_pool is not None
    assert services.session is not None
    assert services.supervisor is not None


def test_crawling_services_registers_metrics_subscriber() -> None:
    services = build_services()

    assert isinstance(
        services.metrics_subscriber,
        CrawlMetricsSubscriber,
    )


@pytest.mark.asyncio
async def test_crawling_services_wires_metrics_subscriber_to_publisher() -> None:
    services = build_services()

    job = CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.com",
        state="Lagos",
        city="Yaba",
        category_slug="restaurants",
    )

    await services.publisher.publish(
        PageCrawledEvent(
            job=job,
            page_number=1,
            companies_found=3,
        )
    )

    snapshot = services.metrics.snapshot()

    assert snapshot.pages_crawled == 1
