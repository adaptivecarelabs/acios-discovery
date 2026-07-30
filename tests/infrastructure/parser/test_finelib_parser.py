from acios_discovery.infrastructure.connectors.finelib.parser import (
    FinelibParser,
)


def test_find_business_cards(
    finelib_health_fixture: str,
) -> None:
    parser = FinelibParser()

    cards = parser.find_business_cards(
        finelib_health_fixture,
    )

    assert len(cards) > 0
