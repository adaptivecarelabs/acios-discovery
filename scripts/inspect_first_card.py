from pathlib import Path

from acios_discovery.infrastructure.connectors.finelib.parser import (
    FinelibParser,
)

fixture = (
    Path("tests")
    / "fixtures"
    / "finelib"
    / "lagos_healthcare_services.html"
)

html = fixture.read_text(encoding="utf-8")

parser = FinelibParser()

cards = parser.find_business_cards(html)

print("Business Cards:", len(cards))
print()

print("First Company:")
print(parser.extract_business_name(cards[0]))
