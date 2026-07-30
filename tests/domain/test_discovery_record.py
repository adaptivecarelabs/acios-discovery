from acios_discovery.domain.discovery import (
    DiscoveryContext,
    DiscoveryRecord,
    RawDiscovery,
)


def test_create_record() -> None:
    company = RawDiscovery(
        source="finelib",
        business_name="Adaptive Care Labs",
    )

    context = DiscoveryContext(
        source="finelib",
        state="Lagos",
        city="Lagos",
        category="Healthcare",
        listing_url="https://example.com",
    )

    record = DiscoveryRecord(
        context=context,
        company=company,
    )

    assert record.company.business_name == "Adaptive Care Labs"

    assert record.context.category == "Healthcare"
