from pathlib import Path

import pytest

from acios_discovery.domain.discovery.context import DiscoveryContext
from acios_discovery.domain.discovery.models import RawDiscovery
from acios_discovery.domain.discovery.record import DiscoveryRecord


@pytest.fixture
def sample_discovery_record() -> DiscoveryRecord:
    return DiscoveryRecord(
        context=DiscoveryContext(
            source="finelib",
            state="Lagos",
            city="Lagos",
            category="Healthcare",
            listing_url="https://www.finelib.com",
        ),
        company=RawDiscovery(
            source="finelib",
            business_name="Drugstoc EHub Ltd",
            detail_url="https://example.com/company",
            address="Ikeja, Lagos",
            phone_numbers=[
                "08030000000",
            ],
            description="Healthcare company",
        ),
    )

@pytest.fixture
def finelib_health_fixture() -> str:
    fixture = (
        Path(__file__).parent
        / "fixtures"
        / "finelib"
        / "lagos_healthcare_services.html"
    )

    return fixture.read_text(
        encoding="utf-8",
    )


@pytest.fixture
def finelib_detail_fixture() -> str:
    fixture = (
        Path(__file__).parent
        / "fixtures"
        / "finelib"
        / "detail"
        / "phytoscience_double_stem_cell.html"
    )

    return fixture.read_text(
        encoding="utf-8",
    )


def load_fixture(path: str) -> str:
    return (
        Path(path)
        .read_text(
            encoding="utf-8",
        )
    )


@pytest.fixture
def lagos_agriculture_service_page1() -> str:
    return load_fixture(
        "tests/fixtures/finelib/pagination/"
        "lagos_agriculture_service_page1.html"
    )


@pytest.fixture
def lagos_agriculture_service_page2() -> str:
    return load_fixture(
        "tests/fixtures/finelib/pagination/"
        "lagos_agriculture_service_page2.html"
    )

@pytest.fixture
def finelib_food_fixture() -> str:
    return load_fixture(
        "tests/fixtures/finelib/"
        "lagos_food_services.html"
    )

@pytest.fixture
def finelib_restaurants_fixture() -> str:
    return load_fixture(
        "tests/fixtures/finelib/"
        "lagos_restaurant_services.html"
    )
