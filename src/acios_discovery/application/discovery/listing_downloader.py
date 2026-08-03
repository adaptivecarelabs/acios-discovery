from acios_discovery.domain.http import HttpClient


class ListingDownloader:

    def __init__(
        self,
        client: HttpClient,
    ) -> None:

        self._client = client

    async def download(
        self,
        url: str,
    ) -> str:

        return await self._client.get(
            url
        )
