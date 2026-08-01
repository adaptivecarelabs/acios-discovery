import httpx

from acios_discovery.domain.http import HttpClient


class HttpxClient(HttpClient):

    async def get(
        self,
        url: str,
    ) -> str:

        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30,
        ) as client:

            response = await client.get(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "(Macintosh; Intel Mac OS X)"
                    )
                },
            )

            response.raise_for_status()

            return response.text
