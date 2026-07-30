from acios_discovery.domain.taxonomy import (
    FINELIB_CATEGORY_MAP,
)


def test_health_mapping() -> None:
    taxonomy = FINELIB_CATEGORY_MAP["health"]

    assert taxonomy.industry == "Healthcare"

    assert taxonomy.sector == "Healthcare Services"

    assert taxonomy.category == "Health Services"
