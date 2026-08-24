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


class ListingNotFoundError(FatalCrawlError):
    """
    A listing page returned 404 for this (city, category)
    combination.

    Distinct from other FatalCrawlErrors: this is an expected,
    routine outcome (most city/category combinations do not
    exist on the source site, and our slug mapping does not
    perfectly predict every city's real URL structure) rather
    than a genuine problem. Callers should treat this as "zero
    results for this job", not as a job failure.
    """
