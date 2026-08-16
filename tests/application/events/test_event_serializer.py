import json

from acios_discovery.application.events.event_serializer import (
    EventSerializer,
)
from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.events.job_completed_event import (
    JobCompletedEvent,
)
from acios_discovery.domain.sources import Source


def make_event() -> JobCompletedEvent:
    job = CrawlJob(
        source=Source.FINELIB,
        listing_url="https://example.com",
        state="Lagos",
        city="Yaba",
        category_slug="restaurants",
    )

    return JobCompletedEvent(
        job=job,
        pages_crawled=2,
        companies_discovered=10,
    )


def test_event_serializer_returns_json_safe_payload() -> None:
    event = make_event()

    payload = EventSerializer.serialize(
        event,
    )

    assert isinstance(payload, dict)

    assert payload["pages_crawled"] == 2
    assert payload["companies_discovered"] == 10

    assert payload["job"]["source"] == "finelib"


def test_event_serializer_returns_json_serializable_payload() -> None:
    event = make_event()

    payload = EventSerializer.serialize(
        event,
    )

    serialized = json.dumps(
        payload,
    )

    assert serialized
