class DiscoveryExecutionService:
    """
    Coordinates one complete discovery run.

    Owns the lifecycle of DiscoveryRun while delegating
    planning, crawling, enrichment, and processing to
    specialised application services.
    """

    def __init__(
        self,
        *,
        planner,
        job_submission_service,
        crawl_supervisor,
        pipeline,
    ) -> None:
        ...
