from __future__ import annotations

from acios_discovery.domain.cac import CacSearchResult
from acios_discovery.domain.http import HttpClient
from acios_discovery.infrastructure.cac.cac_response_parser import (
    CacResponseParser,
)

CAC_SEARCH_URL = (
    "https://authapp.cac.gov.ng/name_similarity_app"
    "/api/public_search/search"
)


class CacSearchClient:
    """
    Searches CAC's public company/business-name register.

    Confirmed empirically: the endpoint requires Origin/Referer
    matching CAC's own frontend (icrp.cac.gov.ng) plus a
    realistic User-Agent — bare requests are rejected with a
    plain 403 (no CAPTCHA, no JS challenge on this specific
    endpoint, unlike the sibling search.cac.gov.ng domain which
    does have a Cloudflare challenge in front of it).

    Rate limited to 5 requests per 60 seconds per source IP,
    confirmed via X-Ratelimit-* response headers and direct
    testing (429 after the 5th request, resets cleanly after
    60s). This client is always used behind ProxyRotatingHttpClient
    (via AdaptiveProxyPool) so that limit is per-proxy, not
    global — the same pattern already used for Finelib.
    """

    def __init__(
        self,
        *,
        http: HttpClient,
        parser: CacResponseParser | None = None,
    ) -> None:
        self._http = http
        self._parser = parser or CacResponseParser()

    async def search(
        self,
        search_term: str,
    ) -> list[CacSearchResult]:

        if not search_term or not search_term.strip():
            raise ValueError(
                "search_term must not be empty",
            )

        payload = await self._http.post_json(
            CAC_SEARCH_URL,
            json={
                "SearchType": "All",
                "searchTerm": search_term.strip(),
            },
            headers={
                "Origin": "https://icrp.cac.gov.ng",
                "Referer": "https://icrp.cac.gov.ng/",
                "Accept": "*/*",
            },
        )

        return self._parser.parse(payload)
