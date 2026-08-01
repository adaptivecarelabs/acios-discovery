from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://www.finelib.com"

OUTPUT = Path("tools/output")
OUTPUT.mkdir(parents=True, exist_ok=True)

print("Downloading business directory...")

html = requests.get(
    f"{BASE}/business",
    timeout=30,
).text

Path("business.html").write_text(
    html,
    encoding="utf-8",
)

soup = BeautifulSoup(html, "html.parser")

rows = []

for link in soup.select("a[href]"):

    href = link["href"]

    text = link.get_text(strip=True)

    if not text:
        continue

    if href.startswith("/business/"):

        slug = href.split("/business/")[1]

    elif href.startswith(f"{BASE}/business/"):

        slug = href.split("/business/")[1]

    else:
        continue

    rows.append(
        (
            slug,
            text,
            urljoin(BASE, href),
        )
    )

rows = sorted(set(rows))

csv = OUTPUT / "finelib_categories.csv"

with csv.open("w", encoding="utf-8") as f:

    f.write("business_slug,name,url\n")

    for slug, name, url in rows:

        f.write(
            f"{slug},{name},{url}\n"
        )

print(f"Discovered {len(rows)} categories")
print(csv.resolve())
