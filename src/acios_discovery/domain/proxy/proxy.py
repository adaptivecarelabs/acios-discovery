from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Proxy:
    """
    A single proxy endpoint from the proxy pool.

    Immutable and hashable so it can key a dict/state map in
    the rate-limiting layer.
    """

    address: str
    port: int
    username: str
    password: str

    @property
    def url(self) -> str:
        """
        Proxy URL in the scheme httpx expects for its
        `proxy=` parameter.
        """
        return (
            f"http://{self.username}:{self.password}"
            f"@{self.address}:{self.port}/"
        )

    def __str__(self) -> str:
        # Never include credentials in logs.
        return f"{self.address}:{self.port}"
