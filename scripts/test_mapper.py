from acios_discovery.infrastructure.connectors.finelib.mapper import (
    FinelibMapper,
)
from acios_discovery.infrastructure.connectors.finelib.parser import (
    FinelibParser,
)
from pathlib import Path


fixture = (
    Path(__file__).parent.parent
    / "tests"
    / "fixtures"
    / "finelib"
    / "lagos_healthcare_services.html"
)

html = fixture.read_text(encoding="utf-8")

parser = FinelibParser()
mapper = FinelibMapper()

cards = parser.find_business_cards(html)

card = cards[0]

print("Business Name")
print(mapper.extract_business_name(card))
print()

print("Detail URL")
print(mapper.extract_detail_url(card))
print()

print("Address")
print(mapper.extract_address(card))
print()

print("Phone Numbers")
print(mapper.extract_phone_numbers(card))
print()

print("Description")
print(mapper.extract_description(card))
