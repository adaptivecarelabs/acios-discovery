from acios_discovery.application.discovery.result import (
    DiscoveryRunResult,
)


def test_result_stores_statistics() -> None:
    result = DiscoveryRunResult(
        source="FINELIB",
        records_found=23,
        records_saved=22,
        duplicates=1,
    )

    assert result.source == "FINELIB"
    assert result.records_found == 23
    assert result.records_saved == 22
    assert result.duplicates == 1


def test_result_defaults_errors() -> None:
    result = DiscoveryRunResult(
        source="FINELIB",
        records_found=0,
        records_saved=0,
    )

    assert result.errors == []
