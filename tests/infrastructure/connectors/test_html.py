from bs4 import BeautifulSoup

from acios_discovery.infrastructure.connectors.html import (
    extract_link,
    extract_text,
)

HTML = """
<div class="card">
    <h2>Adaptive Care Labs</h2>

    <a
        href="https://example.com/company"
    >
        More info
    </a>
</div>
"""


def test_extract_text() -> None:
    soup = BeautifulSoup(
        HTML,
        "lxml",
    )

    assert (
        extract_text(
            soup,
            "h2",
        )
        == "Adaptive Care Labs"
    )


def test_extract_link() -> None:
    soup = BeautifulSoup(
        HTML,
        "lxml",
    )

    assert (
        extract_link(
            soup,
            "a",
        )
        == "https://example.com/company"
    )
