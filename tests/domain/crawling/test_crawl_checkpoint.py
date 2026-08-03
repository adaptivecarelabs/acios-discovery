from acios_discovery.domain.crawling.crawl_checkpoint import (
    CrawlCheckpoint,
)


def test_checkpoint_fields():

    checkpoint = CrawlCheckpoint(
        session_id="session-1",
        state="Lagos",
        city="Yaba",
        category_slug="restaurants",
        page=4,
    )

    assert checkpoint.session_id == "session-1"

    assert checkpoint.page == 4

    assert checkpoint.city == "Yaba"
