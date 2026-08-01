from acios_discovery.domain.taxonomy import (
    FINELIB_CATEGORY_MAP,
)


def test_health_mapping() -> None:
    taxonomy = FINELIB_CATEGORY_MAP["healthcare"]

    assert taxonomy.industry == "Healthcare"
    assert taxonomy.sector == "Healthcare"
    assert taxonomy.category == "Healthcare"
