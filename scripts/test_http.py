import asyncio

from acios_discovery.infrastructure.http.httpx_client import HttpxClient


async def main():
    client = HttpxClient()

    html = await client.get(
        "https://www.finelib.com/cities/lagos/health"
    )

    print(len(html))
    print(html[:500])


asyncio.run(main())
