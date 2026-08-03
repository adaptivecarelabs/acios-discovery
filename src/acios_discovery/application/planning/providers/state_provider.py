from __future__ import annotations

import json
from pathlib import Path


class StateProvider:

    def __init__(self) -> None:

        root = Path(__file__).resolve().parents[3]

        self._path = (
            root
            / "data"
            / "nigeria_states.json"
        )

    def get_states(
        self,
    ) -> list[str]:

        with self._path.open(
            encoding="utf-8",
        ) as file:

            return json.load(file)
