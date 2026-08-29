from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any


class HttpClient(ABC):

    @abstractmethod
    async def get(
        self,
        url: str,
    ) -> str:
        """
        Download an HTML page.
        """

    @abstractmethod
    async def post_json(
        self,
        url: str,
        *,
        json: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> Any:
        """
        POST a JSON body and return the parsed JSON response.
        """
