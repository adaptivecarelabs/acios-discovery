from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://www.finelib.com"

OUTPUT = Path("tools/output")
OUTPUT.mkdir(
    parents=True,
    exist_ok=True,
)

ROOT_SECTIONS = [
    {
        "root": "business",
        "url": f"{BASE}/business",
    },
    {
        "root": "agriculture",
        "url": f"{BASE}/agriculture",
    },
    {
        "root": "accommodation",
        "url": f"{BASE}/accommodation",
    },
    {
        "root": "education",
        "url": f"{BASE}/education",
    },
    {
        "root": "travel",
        "url": f"{BASE}/travel",
    },
]

rows: list[tuple[str, str, str, str]] = []

for section in ROOT_SECTIONS:

    root = section["root"]
    url = section["url"]

    print(f"Downloading {root} directory...")

    response = requests.get(
        url,
        timeout=30,
    )

    if response.status_code != 200:
        print(f"  -> skipped ({response.status_code})")
        continue

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    prefix = f"/{root}/"

    found = 0

    for link in soup.select("a[href]"):

        href = link["href"]

        text = link.get_text(strip=True)

        if not text:
            continue

        if href.startswith(prefix):

            slug = href[len(prefix):]

        elif href.startswith(f"{BASE}{prefix}"):

            slug = href[len(f"{BASE}{prefix}"):]

        else:
            continue

        slug = slug.strip("/")

        if not slug:
            continue

        if "/" in slug:
            continue

        rows.append(
            (
                root,
                slug,
                text,
                urljoin(BASE, href),
            )
        )

        found += 1

    print(f"  -> found {found} category links")

rows = sorted(set(rows))

csv = OUTPUT / "finelib_categories.csv"

with csv.open(
    "w",
    encoding="utf-8",
) as f:

    f.write("root,business_slug,name,url\n")

    for root, slug, name, url in rows:

        f.write(
            f"{root},{slug},{name},{url}\n"
        )

print()

print(f"Discovered {len(rows)} unique categories")

print(csv.resolve())
