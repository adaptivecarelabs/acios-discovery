from pathlib import Path

from acios_discovery.infrastructure.connectors.finelib.detail_mapper import (
    FinelibDetailMapper,
)
from acios_discovery.infrastructure.connectors.finelib.detail_parser import (
    FinelibDetailParser,
)

FIXTURE = (
    Path(__file__).parent.parent.parent
    / "fixtures"
    / "finelib"
    / "detail"
    / "phytoscience_double_stem_cell.html"
)


def load_soup():
    html = FIXTURE.read_text(
        encoding="utf-8",
    )

    parser = FinelibDetailParser()

    return parser.parse(
        html,
    )


def test_default_email() -> None:
    mapper = FinelibDetailMapper()

    assert mapper.extract_email(
        load_soup(),
    ) == "natureregenerative@gmail.com"


def test_default_website() -> None:
    mapper = FinelibDetailMapper()

    assert mapper.extract_website(
        load_soup(),
    ) == "https://natureregenerative.com/"


def test_default_social_links() -> None:
    mapper = FinelibDetailMapper()

    assert mapper.extract_social_links(
        load_soup(),
    ) == {
        "facebook": "https://web.facebook.com/Stemcelldistributors",
        "twitter": "https://twitter.com/Cellregenerativ",
    }


def test_default_year_founded() -> None:
    mapper = FinelibDetailMapper()

    assert mapper.extract_year_founded(
        load_soup(),
    ) == 2012


def test_default_employee_count() -> None:
    mapper = FinelibDetailMapper()

    assert mapper.extract_employee_count(
        load_soup(),
    ) == "20 and upwards"


def test_default_business_locations() -> None:
    mapper = FinelibDetailMapper()

    assert mapper.extract_business_locations(
        load_soup(),
    ) == 23


def test_default_product_types() -> None:
    mapper = FinelibDetailMapper()

    assert mapper.extract_product_types(
        load_soup(),
    ) == [
        "Stemcell therapy",
        "Stemcell products",
        "Beauty products",
    ]


def test_default_payment_methods() -> None:
    mapper = FinelibDetailMapper()

    assert mapper.extract_payment_methods(
        load_soup(),
    ) == [
        "cash",
        "bank transfer",
        "master card",
        "debit card",
    ]
