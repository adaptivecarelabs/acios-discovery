from __future__ import annotations

from datetime import UTC, datetime

from acios_discovery.domain.events.crawl_event import CrawlEvent


def test_crawl_event_sets_occurred_at_automatically() -> None:
    event = CrawlEvent()

    assert isinstance(
        event.occurred_at,
        datetime,
    )

    assert event.occurred_at.tzinfo == UTC


def test_crawl_event_accepts_explicit_occurred_at() -> None:
    occurred_at = datetime(
        2026,
        1,
        1,
        12,
        0,
        tzinfo=UTC,
    )

    event = CrawlEvent(
        occurred_at=occurred_at,
    )

    assert event.occurred_at == occurred_at


def test_crawl_event_type_returns_class_name() -> None:
    event = CrawlEvent()

    assert event.event_type == "CrawlEvent"
