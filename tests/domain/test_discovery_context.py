from acios_discovery.domain.discovery import (
    DiscoveryContext,
)


def test_create_context() -> None:
    context = DiscoveryContext(
        source="finelib",
        state="Lagos",
        city="Lagos",
        category="Healthcare",
        listing_url="https://www.finelib.com/cities/lagos/health",
    )

    assert context.source == "finelib"

    assert context.state == "Lagos"

    assert context.city == "Lagos"

    assert context.category == "Healthcare"

    assert context.country == "Nigeria"
