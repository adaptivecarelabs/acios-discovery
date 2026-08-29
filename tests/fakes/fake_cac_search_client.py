from __future__ import annotations

from acios_discovery.domain.cac import CacSearchResult


class FakeCacSearchClient:
    """
    Fake CacSearchClient used by tests.

    Returns candidates based on the requested search term,
    never performing a real HTTP request. Duck-types
    CacSearchClient's public interface (search()) rather than
    inheriting from it, since CacSearchClient is a concrete
    infrastructure class, not an ABC.
    """

    def __init__(
        self,
        responses: dict[str, list[CacSearchResult]],
    ) -> None:
        self._responses = responses
        self.requests: list[str] = []

    async def search(
        self,
        search_term: str,
    ) -> list[CacSearchResult]:

        self.requests.append(search_term)

        return self._responses.get(search_term, [])
