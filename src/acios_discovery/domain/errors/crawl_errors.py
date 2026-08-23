from __future__ import annotations


class CrawlError(Exception):
    """
    Base class for crawl-pipeline errors that carry a deliberate
    retryable/fatal classification.

    Any exception NOT deriving from this hierarchy (a bug, an
    unexpected parse failure, etc.) is treated as non-retryable
    by default — retrying an unclassified failure risks infinite
    loops or duplicate side effects, so the safe default is
    fail-fast, not blind retry.
    """


class RetryableCrawlError(CrawlError):
    """
    A transient failure (timeout, connection error, 5xx, 429)
    where retrying the same job again is reasonable.
    """


class FatalCrawlError(CrawlError):
    """
    A failure where retrying the same job would not help
    (4xx other than 429, malformed request, etc).
    """
