from __future__ import annotations

import httpx

from acios_discovery.domain.proxy import Proxy, ProxyProvider
from acios_discovery.shared.logging import logger

WEBSHARE_API_BASE = "https://proxy.webshare.io/api/v2"


class WebshareProxyProvider(ProxyProvider):
    """
    Fetches the account's owned proxy pool from Webshare's
    Proxy List API.

    Uses the account API key (Authorization: Token ...), which
    is distinct from any individual proxy's username/password
    used to actually route crawl traffic through that proxy.
    """

    def __init__(
        self,
        *,
        api_key: str,
        page_size: int = 100,
    ) -> None:
        self._api_key = api_key
        self._page_size = page_size

    async def list_proxies(self) -> list[Proxy]:

        proxies: list[Proxy] = []

        url: str | None = (
            f"{WEBSHARE_API_BASE}/proxy/list/"
            f"?mode=direct&page=1&page_size={self._page_size}"
        )

        async with httpx.AsyncClient(
            headers={
                "Authorization": f"Token {self._api_key}",
            },
            timeout=10,
        ) as client:

            while url is not None:

                response = await client.get(url)

                response.raise_for_status()

                payload = response.json()

                for entry in payload.get("results", []):

                    if not entry.get("valid", True):
                        continue

                    proxies.append(
                        Proxy(
                            address=entry["proxy_address"],
                            port=int(entry["port"]),
                            username=entry["username"],
                            password=entry["password"],
                        )
                    )

                url = payload.get("next")

        logger.info(
            "Fetched %d proxies from Webshare",
            len(proxies),
        )

        return proxies
