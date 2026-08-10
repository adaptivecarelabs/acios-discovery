from __future__ import annotations

from collections.abc import Callable

from acios_discovery.application.crawling.crawl_worker import (
    CrawlWorker,
)

CrawlWorkerFactory = Callable[[], CrawlWorker]
