from pathlib import Path

import pytest


@pytest.fixture
def finelib_health_fixture() -> str:
    fixture = (
        Path(__file__).parent
        / "fixtures"
        / "finelib"
        / "lagos_healthcare_services.html"
    )

    return fixture.read_text(encoding="utf-8")
