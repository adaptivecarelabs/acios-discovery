from acios_discovery.domain.sources import Source


def test_source_enum() -> None:
    assert Source.FINELIB == "finelib"

    assert Source.CONNECT_NIGERIA == "connect_nigeria"
