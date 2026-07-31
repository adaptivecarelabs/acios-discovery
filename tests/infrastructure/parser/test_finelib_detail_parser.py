from pathlib import Path

from bs4 import BeautifulSoup

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


def test_detail_parser_returns_beautiful_soup() -> None:
    html = FIXTURE.read_text(
        encoding="utf-8",
    )

    parser = FinelibDetailParser()

    soup = parser.parse(
        html,
    )

    assert isinstance(
        soup,
        BeautifulSoup,
    )

    assert soup.title is not None

    assert soup.title.text.strip() != ""
