from __future__ import annotations

import json
from pathlib import Path


class UnknownStateError(ValueError):
    """
    Raised when a state name doesn't match any state in
    nigeria_cities.json, after case-insensitive normalization.
    """


class CityProvider:
    def __init__(self) -> None:
        root = Path(__file__).resolve().parents[3]

        self._path = (
            root
            / "data"
            / "nigeria_cities.json"
        )

    def _load_cities_by_normalized_state(
        self,
    ) -> dict[str, tuple[str, list[str]]]:
        """
        Returns a mapping of normalized (lowercased, stripped)
        state name -> (original-cased state name, city list),
        so lookups are case-insensitive while callers still get
        back the canonical state name as stored in the data file.
        """

        with self._path.open(
            encoding="utf-8",
        ) as file:
            cities = json.load(file)

        return {
            state.strip().lower(): (state, city_list)
            for state, city_list in cities.items()
        }

    def get_cities(
        self,
        state: str,
    ) -> list[str]:
        """
        Return the list of cities/LGAs for a state.

        Matching is case-insensitive ("lagos", "Lagos", "LAGOS"
        all resolve to the same entry) and ignores surrounding
        whitespace.

        Raises UnknownStateError if the state doesn't match any
        entry in nigeria_cities.json — silently returning an
        empty list here previously caused --state typos (or
        wrong casing) to produce a crawl with zero plans and no
        indication of why.
        """

        normalized = state.strip().lower()

        by_state = self._load_cities_by_normalized_state()

        if normalized not in by_state:
            available = ", ".join(
                sorted(
                    original
                    for original, _ in by_state.values()
                )
            )

            raise UnknownStateError(
                f"Unknown state '{state}'. "
                f"Available states: {available}"
            )

        _canonical_name, city_list = by_state[normalized]

        return city_list

    def canonical_state_name(
        self,
        state: str,
    ) -> str:
        """
        Return the correctly-cased state name for a given
        (possibly differently-cased) state input — e.g.
        "rivers" -> "Rivers". Useful for callers that want to
        display or store the canonical form.
        """

        normalized = state.strip().lower()

        by_state = self._load_cities_by_normalized_state()

        if normalized not in by_state:
            raise UnknownStateError(
                f"Unknown state '{state}'.",
            )

        canonical_name, _city_list = by_state[normalized]

        return canonical_name
