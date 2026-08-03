from __future__ import annotations

import json
from pathlib import Path


class CityProvider:
    def __init__(self) -> None:
        root = Path(__file__).resolve().parents[3]

        self._path = (
            root
            / "data"
            / "nigeria_cities.json"
        )

    def get_cities(
        self,
        state: str,
    ) -> list[str]:
        with self._path.open(
            encoding="utf-8",
        ) as file:
            cities = json.load(file)

        return cities.get(
            state,
            [],
        )
