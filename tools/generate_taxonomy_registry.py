from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OUTPUT = ROOT / "tools" / "output"

CATEGORIES = OUTPUT / "finelib_categories.csv"
SUBCATEGORIES = OUTPUT / "finelib_subcategories.csv"

REGISTRY = (
    ROOT
    / "src"
    / "acios_discovery"
    / "domain"
    / "taxonomy"
    / "registry.py"
)


def load_categories() -> dict[str, str]:
    categories = {}

    with CATEGORIES.open(
        newline="",
        encoding="utf-8",
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:
            categories[row["business_slug"]] = {
                "root": row["root"],
                "name": row["name"],
        }

    return categories


def load_subcategories():
    with SUBCATEGORIES.open(
        newline="",
        encoding="utf-8",
    ) as f:
        return list(csv.DictReader(f))


def generate_registry() -> str:
    categories = load_categories()
    subcategories = load_subcategories()

    lines = []

    lines.append("from .models import Taxonomy")
    lines.append("")
    lines.append("FINELIB_CATEGORY_MAP: dict[str, Taxonomy] = {")

    for slug, data in sorted(categories.items()):

        name = data["name"]
        root = data["root"]

        lines.append(f'    "{slug}": Taxonomy(')
        lines.append(f'        root="{root}",')
        lines.append(f'        industry="{name}",')
        lines.append(f'        sector="{name}",')
        lines.append(f'        category="{name}",')
        lines.append("    ),")

    seen: set[str] = set()

    for row in sorted(
        subcategories,
        key=lambda r: (r["subcategory_slug"], r["parent"]),
    ):

        slug= row["subcategory_slug"]

        if slug in seen:
            continue

        seen.add(slug)
        parent = categories[row["parent"]]

        parent_name = parent["name"]
        parent_root = parent["root"]

        lines.append(
            f'    "{slug}": Taxonomy('
        )
        lines.append(f'        root="{parent_root}",')
        lines.append(f'        industry="{parent_name}",')
        lines.append(f'        sector="{parent_name}",')
        lines.append(f'        category="{parent_name}",')
        lines.append(f'        subcategory="{row["name"]}",')
        lines.append("    ),")

    lines.append("}")

    return "\n".join(lines)


def main():
    REGISTRY.write_text(
        generate_registry(),
        encoding="utf-8",
    )

    print(f"Wrote {REGISTRY}")


if __name__ == "__main__":
    main()
