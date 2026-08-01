from acios_discovery.domain.http import HttpClient


class FakeHttpClient(HttpClient):
    """
    Fake HTTP client used by tests.

    Returns HTML based on the requested URL.
    """

    def __init__(
        self,
        responses: dict[str, str],
    ) -> None:

        self._responses = responses

    async def get(
        self,
        url: str,
    ) -> str:

        try:
            return self._responses[url]

        except KeyError as exc:
            raise AssertionError(
                f"No fake response configured for URL: {url}"
            ) from exc
