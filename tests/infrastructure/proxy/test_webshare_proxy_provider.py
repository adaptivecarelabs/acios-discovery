from __future__ import annotations

import httpx
import pytest

from acios_discovery.infrastructure.proxy import WebshareProxyProvider


@pytest.mark.asyncio
async def test_list_proxies_parses_single_page(respx_mock=None):
    """
    Uses httpx's MockTransport instead of a network mock library,
    since none is currently a project dependency.
    """

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Token test-key"

        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "proxy_address": "1.2.3.4",
                        "port": 8080,
                        "username": "u1",
                        "password": "p1",
                        "valid": True,
                    },
                    {
                        "proxy_address": "5.6.7.8",
                        "port": 9090,
                        "username": "u2",
                        "password": "p2",
                        "valid": True,
                    },
                ],
                "next": None,
            },
        )

    transport = httpx.MockTransport(handler)

    provider = WebshareProxyProvider(api_key="test-key")

    # Monkeypatch the client construction to use our mock transport
    original_async_client = httpx.AsyncClient

    def patched_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_async_client(*args, **kwargs)

    import acios_discovery.infrastructure.proxy.webshare_proxy_provider as module

    module.httpx.AsyncClient = patched_client

    try:
        proxies = await provider.list_proxies()
    finally:
        module.httpx.AsyncClient = original_async_client

    assert len(proxies) == 2
    assert proxies[0].address == "1.2.3.4"
    assert proxies[0].port == 8080
    assert proxies[1].address == "5.6.7.8"


@pytest.mark.asyncio
async def test_list_proxies_skips_invalid_entries():

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "proxy_address": "1.2.3.4",
                        "port": 8080,
                        "username": "u1",
                        "password": "p1",
                        "valid": True,
                    },
                    {
                        "proxy_address": "5.6.7.8",
                        "port": 9090,
                        "username": "u2",
                        "password": "p2",
                        "valid": False,
                    },
                ],
                "next": None,
            },
        )

    transport = httpx.MockTransport(handler)

    provider = WebshareProxyProvider(api_key="test-key")

    original_async_client = httpx.AsyncClient

    def patched_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_async_client(*args, **kwargs)

    import acios_discovery.infrastructure.proxy.webshare_proxy_provider as module

    module.httpx.AsyncClient = patched_client

    try:
        proxies = await provider.list_proxies()
    finally:
        module.httpx.AsyncClient = original_async_client

    assert len(proxies) == 1
    assert proxies[0].address == "1.2.3.4"


@pytest.mark.asyncio
async def test_list_proxies_follows_pagination():

    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1

        if call_count == 1:
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "proxy_address": "1.1.1.1",
                            "port": 1000,
                            "username": "u",
                            "password": "p",
                            "valid": True,
                        },
                    ],
                    "next": "https://proxy.webshare.io/api/v2/proxy/list/?page=2",
                },
            )

        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "proxy_address": "2.2.2.2",
                        "port": 2000,
                        "username": "u",
                        "password": "p",
                        "valid": True,
                    },
                ],
                "next": None,
            },
        )

    transport = httpx.MockTransport(handler)

    provider = WebshareProxyProvider(api_key="test-key")

    original_async_client = httpx.AsyncClient

    def patched_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_async_client(*args, **kwargs)

    import acios_discovery.infrastructure.proxy.webshare_proxy_provider as module

    module.httpx.AsyncClient = patched_client

    try:
        proxies = await provider.list_proxies()
    finally:
        module.httpx.AsyncClient = original_async_client

    assert call_count == 2
    assert len(proxies) == 2
    assert {p.address for p in proxies} == {"1.1.1.1", "2.2.2.2"}
