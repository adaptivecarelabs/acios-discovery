import pytest

from acios_discovery.infrastructure.connectors.finelib.listing_parser import (
    FinelibParser,
)


@pytest.mark.parametrize(
    (
        "fixture_name",
        "expected",
    ),
    [
        (
            "lagos_agriculture_service_page1",
            True,
        ),
        (
            "lagos_agriculture_service_page2",
            False,
        ),
    ],
)
def test_next_page_url_exists(
    fixture_name: str,
    expected: bool,
    request: pytest.FixtureRequest,
) -> None:

    html = request.getfixturevalue(
        fixture_name,
    )

    parser = FinelibParser()

    current_url = (
        "https://www.finelib.com/"
        "cities/lagos/agriculture"
    )

    result = parser.next_page_url(
        html,
        current_url,
    )

    assert (
        result is not None
    ) is expected


def test_next_page_url_returns_page_two(
    lagos_agriculture_service_page1: str,
) -> None:

    parser = FinelibParser()

    current_url = (
        "https://www.finelib.com/"
        "cities/lagos/agriculture"
    )

    assert (
        parser.next_page_url(
            lagos_agriculture_service_page1,
            current_url,
        )
        == (
            "https://www.finelib.com/"
            "cities/lagos/agriculture/page-2"
        )
    )


def test_next_page_url_returns_none_on_last_page(
    lagos_agriculture_service_page2: str,
) -> None:

    parser = FinelibParser()

    current_url = (
        "https://www.finelib.com/"
        "cities/lagos/agriculture/page-2"
    )

    assert (
        parser.next_page_url(
            lagos_agriculture_service_page2,
            current_url,
        )
        is None
    )


def test_next_page_url_resolves_relative_url(
    lagos_agriculture_service_page1: str,
) -> None:

    parser = FinelibParser()

    current_url = (
        "https://www.finelib.com/"
        "cities/lagos/agriculture"
    )

    result = parser.next_page_url(
        lagos_agriculture_service_page1,
        current_url,
    )

    assert result == (
        "https://www.finelib.com/"
        "cities/lagos/agriculture/page-2"
    )
