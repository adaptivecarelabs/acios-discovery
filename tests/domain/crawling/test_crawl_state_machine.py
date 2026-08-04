import pytest

from acios_discovery.domain.crawling.crawl_state import CrawlState
from acios_discovery.domain.crawling.crawl_state_machine import (
    CrawlStateMachine,
    InvalidStateTransition,
)


def test_happy_path():

    machine = CrawlStateMachine()

    machine.initialize()

    machine.start()

    machine.pause()

    machine.resume()

    machine.start()

    machine.complete()

    assert machine.state == CrawlState.COMPLETED


def test_invalid_transition():

    machine = CrawlStateMachine()

    with pytest.raises(
        InvalidStateTransition,
    ):

        machine.complete()


def test_cancel():

    machine = CrawlStateMachine()

    machine.cancel()

    assert machine.state == CrawlState.CANCELLED


def test_fail():

    machine = CrawlStateMachine()

    machine.initialize()

    machine.fail()

    assert machine.state == CrawlState.FAILED
