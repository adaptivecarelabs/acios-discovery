import httpx

from acios_discovery.domain.html import HtmlClient


class RequestsHtmlClient(HtmlClient):

    async def get(
        self,
        url: str,
    ) -> str:

        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30,
        ) as client:

            response = await client.get(url)

            response.raise_for_status()

            return response.text
