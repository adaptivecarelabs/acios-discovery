from __future__ import annotations

import logging

from rich.console import Console
from rich.logging import RichHandler


def configure_logging(
    console: Console | None = None,
) -> None:
    """
    Configure root logging.

    When a rich Console is supplied, logging routes through
    RichHandler bound to that console. rich.progress.Progress
    (a Live display) cooperates with Console output: a log line
    printed while a progress bar is active is inserted cleanly
    above the bar rather than corrupting it. Plain
    logging.StreamHandler does not have this property, so it is
    only used when no console is supplied (non-interactive
    entrypoints).
    """

    if console is not None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[
                RichHandler(
                    console=console,
                    show_path=False,
                    rich_tracebacks=True,
                )
            ],
        )
        return

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)-8s | "
            "%(name)s | "
            "%(message)s"
        ),
    )


logger = logging.getLogger("acios")
