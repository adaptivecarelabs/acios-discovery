from pathlib import Path

from bs4 import BeautifulSoup

fixture = Path("tests/fixtures/finelib/lagos_healthcare_services.html")

soup = BeautifulSoup(fixture.read_text(encoding="utf-8"), "lxml")

listing = soup.find("div", class_="listing-info-img")

assert listing is not None

print("=" * 80)
print("PARENT")
print("=" * 80)
print(listing.parent.prettify()[:4000])

print()
print("=" * 80)
print("GRANDPARENT")
print("=" * 80)
print(listing.parent.parent.prettify()[:6000])
