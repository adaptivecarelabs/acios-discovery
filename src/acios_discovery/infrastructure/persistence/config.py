from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def _require_database_url() -> str:
    value = os.getenv("DATABASE_URL")

    if not value:
        raise RuntimeError(
            "DATABASE_URL must be set before starting the application."
        )

    return value


DATABASE_URL: str = _require_database_url()

WEBSHARE_API_KEY: str | None = os.getenv("WEBSHARE_API_KEY")
