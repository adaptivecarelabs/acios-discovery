from acios_discovery.infrastructure.connectors.finelib.mapper import (
    FinelibMapper,
)
from acios_discovery.infrastructure.connectors.finelib.parser import (
    FinelibParser,
)


def test_mapper_extracts_business_name(
    finelib_health_fixture: str,
) -> None:
    parser = FinelibParser()

    mapper = FinelibMapper()

    cards = parser.find_business_cards(
        finelib_health_fixture,
    )

    name = mapper.extract_business_name(cards[0])

    assert name == "Phytoscience Double Stem Cell"


def test_mapper_creates_raw_discovery(
    finelib_health_fixture: str,
) -> None:
    parser = FinelibParser()

    mapper = FinelibMapper()

    cards = parser.find_business_cards(
        finelib_health_fixture,
    )

    discovery = mapper.map(cards[0])

    assert discovery.source == "finelib"

    assert (
        discovery.business_name
        == "Phytoscience Double Stem Cell"
    )

    assert (
        discovery.detail_url
        == "https://www.finelib.com/listing/Phytoscience-Double-Stem-Cell/101646/"
    )



def test_mapper_extracts_detail_url(
    finelib_health_fixture: str,
) -> None:
    parser = FinelibParser()

    mapper = FinelibMapper()

    cards = parser.find_business_cards(
        finelib_health_fixture,
    )

    url = mapper.extract_detail_url(cards[0])

    assert (
        url
        == "https://www.finelib.com/listing/Phytoscience-Double-Stem-Cell/101646/"
    )


def test_mapper_extracts_address(
    finelib_health_fixture: str,
) -> None:
    parser = FinelibParser()

    mapper = FinelibMapper()

    cards = parser.find_business_cards(
        finelib_health_fixture,
    )

    address = mapper.extract_address(
        cards[0]
    )

    assert (
        address
        == "No. 23 Opebi Road, Opebi- Ikeja, Lagos"
    )


def test_mapper_maps_address(
    finelib_health_fixture: str,
) -> None:
    parser = FinelibParser()

    mapper = FinelibMapper()

    cards = parser.find_business_cards(
        finelib_health_fixture,
    )

    discovery = mapper.map(
        cards[0]
    )

    assert (
        discovery.address
        == "No. 23 Opebi Road, Opebi- Ikeja, Lagos"
    )

def test_mapper_extracts_phone_numbers(
    finelib_health_fixture: str,
) -> None:
    parser = FinelibParser()

    mapper = FinelibMapper()

    cards = parser.find_business_cards(
        finelib_health_fixture,
    )

    numbers = mapper.extract_phone_numbers(
        cards[0],
    )

    assert numbers == [
        "0803 285 2530",
        "0814 966 6894",
        "0803 285 2530",
    ]


def test_mapper_maps_phone_numbers(
    finelib_health_fixture: str,
) -> None:
    parser = FinelibParser()

    mapper = FinelibMapper()

    cards = parser.find_business_cards(
        finelib_health_fixture,
    )

    discovery = mapper.map(
        cards[0],
    )

    assert discovery.phone_numbers == [
        "0803 285 2530",
        "0814 966 6894",
        "0803 285 2530",
    ]


def test_mapper_extracts_description(
    finelib_health_fixture: str,
) -> None:
    parser = FinelibParser()
    mapper = FinelibMapper()

    cards = parser.find_business_cards(
        finelib_health_fixture,
    )

    description = mapper.extract_description(
        cards[0],
    )

    assert description.startswith(
        "Phytoscience Double Stem Cell is a global"
    )
