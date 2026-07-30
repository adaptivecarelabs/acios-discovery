from pathlib import Path

import pytest

from acios_discovery.infrastructure.parser.finelib.parser import FinelibParser

FIXTURE = (
    Path(__file__)
    .parents[2]
    / "fixtures"
    / "finelib"
    / "lagos_healthcare_services.html"
)


def test_fixture_exists() -> None:
    assert FIXTURE.exists()


def test_parser_not_implemented() -> None:
    html = FIXTURE.read_text(encoding="utf-8")

    parser = FinelibParser()

    with pytest.raises(NotImplementedError):
        parser.parse(html)
