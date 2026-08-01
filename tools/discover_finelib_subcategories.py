from __future__ import annotations

import csv
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://www.finelib.com"

INPUT = Path("tools/output/finelib_categories.csv")
OUTPUT = Path("tools/output/finelib_subcategories.csv")

rows = []

categories = list(csv.DictReader(INPUT.open()))

for category in categories:

    url = category["url"]

    print(f"Scanning {url}")

    html = requests.get(url, timeout=30).text

    soup = BeautifulSoup(html, "html.parser")

    seen = set()

    for a in soup.select("a[href]"):

        href = a["href"]

        if not href.startswith("/business/"):
            continue

        slug = href.split("/")[-1]

        if slug == category["business_slug"]:
            continue

        if slug in seen:
            continue

        seen.add(slug)

        rows.append(
            {
                "parent": category["business_slug"],
                "subcategory_slug": slug,
                "name": a.get_text(strip=True),
                "url": BASE + href,
            }
        )

    time.sleep(1)

OUTPUT.parent.mkdir(exist_ok=True)

with OUTPUT.open(
    "w",
    newline="",
    encoding="utf-8",
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "parent",
            "subcategory_slug",
            "name",
            "url",
        ],
    )

    writer.writeheader()

    writer.writerows(rows)

print()
print(f"Discovered {len(rows)} subcategories")
print(OUTPUT.resolve())


