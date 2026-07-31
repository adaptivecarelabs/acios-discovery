from pathlib import Path

from acios_discovery.domain.discovery.discovery import Discovery
from acios_discovery.infrastructure.connectors.finelib.detail_mapper import (
    FinelibDetailMapper,
)
from acios_discovery.infrastructure.connectors.finelib.detail_parser import (
    FinelibDetailParser,
)
from acios_discovery.infrastructure.connectors.finelib.listing_mapper import (
    FinelibMapper,
)
from acios_discovery.infrastructure.connectors.finelib.listing_parser import (
    FinelibParser,
)


def section(title: str) -> None:
    print(title)
    print("-" * 80)


#
# Load Listing Page
#

listing_fixture = (
    Path(__file__).parent.parent
    / "tests"
    / "fixtures"
    / "finelib"
    / "lagos_healthcare_services.html"
)

listing_html = listing_fixture.read_text(
    encoding="utf-8",
)

detail_fixture = (
    Path(__file__).parent.parent
    / "tests"
    / "fixtures"
    / "finelib"
    / "detail"
    / "phytoscience_double_stem_cell.html"
)

detail_html = detail_fixture.read_text(
    encoding="utf-8",
)

listing_parser = FinelibParser()
listing_mapper = FinelibMapper()
detail_parser = FinelibDetailParser()
detail_mapper = FinelibDetailMapper()

cards = listing_parser.find_business_cards(
    listing_html,
)

print("=" * 80)
print(f"Businesses Found: {len(cards)}")
print("=" * 80)
print()

card = cards[0]
detail = detail_parser.parse(detail_html)

discovery = Discovery(
    business_name=listing_mapper.extract_business_name(card),
    detail_url=listing_mapper.extract_detail_url(card),
    address=listing_mapper.extract_address(card),
    description=listing_mapper.extract_description(card),
    phone_numbers=listing_mapper.extract_phone_numbers(card),
    email=detail_mapper.extract_email(detail),
    website=detail_mapper.extract_website(detail),
    social_links=detail_mapper.extract_social_links(detail),
    year_founded=detail_mapper.extract_year_founded(detail),
    employee_count=detail_mapper.extract_employee_count(detail),
    business_locations=detail_mapper.extract_business_locations(detail),
    product_types=detail_mapper.extract_product_types(detail),
    payment_methods=detail_mapper.extract_payment_methods(detail),
)

section("Business Name")
print(listing_mapper.extract_business_name(card))
print()

section("Detail URL")
detail_url = listing_mapper.extract_detail_url(card)
print(detail_url)
print()

section("Address")
print(listing_mapper.extract_address(card))
print()

section("Phone Numbers")
phones = listing_mapper.extract_phone_numbers(card)

if phones:
    for phone in phones:
        print(phone)
else:
    print(None)

print()

section("Description")
print(listing_mapper.extract_description(card))
print()

#
# Load Detail Page
#

detail_fixture = (
    Path(__file__).parent.parent
    / "tests"
    / "fixtures"
    / "finelib"
    / "detail"
    / "phytoscience_double_stem_cell.html"
)

detail_html = detail_fixture.read_text(
    encoding="utf-8",
)

detail = detail_parser.parse(
    detail_html,
)

section("Email")
print(discovery.email)
print()

section("Website")
print(discovery.website)
print()

section("Social Links")

socials = detail_mapper.extract_social_links(
    detail,
)

if socials:
    for platform, url in socials.items():
        print(f"{platform}: {url}")
else:
    print(None)

print()

section("Year Founded")
print(discovery.year_founded)
print()

section("Employee Count")
print(discovery.employee_count)
print()

section("Business Locations")
print(discovery.business_locations)
print()

section("Product Types")

products = detail_mapper.extract_product_types(
    detail,
)

if products:
    for product in products:
        print(product)
else:
    print(None)

print()

section("Payment Methods")

payments = detail_mapper.extract_payment_methods(
    detail,
)

if payments:
    for payment in payments:
        print(payment)
else:
    print(None)


print()
print("=" * 80)
print("DISCOVERY OBJECT")
print("=" * 80)

print(discovery)
