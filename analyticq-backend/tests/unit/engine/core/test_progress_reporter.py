import logging
from unittest.mock import Mock

import pytest
from analyticq.engine.core import ProgressReporter


@pytest.fixture
def reporter():
    return ProgressReporter()


def test_initial__reporter_state(reporter):
    assert len(reporter.progress_callback) == 0
    assert isinstance(reporter.logger, logging.Logger)


def test_add_single_progress_callback(reporter):
    callback_mock = Mock()
    reporter.add_progress_callback(callback_mock)
    assert len(reporter.progress_callback) == 1, "Expected one callback added"
    assert callback_mock in reporter.progress_callback, "Expected callback inside callback list"


def test_add_multiple_callbacks(reporter):
    callbacks = [Mock() for _ in range(3)]

    for callback_mock in callbacks:
        reporter.add_progress_callback(callback_mock)

    assert len(reporter.progress_callback) == 3, "Expected 3 callbacks added"
    for callback_mock in callbacks:
        assert callback_mock in reporter.progress_callback, "Expected callback inside callback list"


@pytest.mark.asyncio
async def test_notify_progress(reporter):
    callbacks = [Mock() for _ in range(2)]

    for callback in callbacks:
        reporter.add_progress_callback(callback)

    test_message = "Processing item 1 of 10"
    test_percentage = 0.1

    await reporter.notify_progress(test_message, test_percentage)

    for callback in callbacks:
        callback.assert_called_once_with(test_message, test_percentage)


@pytest.mark.asyncio
async def test_notify_progress_with_failing_callback(reporter, caplog):

    normal_callback = Mock()
    failing_callback = Mock(side_effect=Exception("Callback failed"))

    reporter.add_progress_callback(normal_callback)
    reporter.add_progress_callback(failing_callback)

    with caplog.at_level(logging.ERROR):
        await reporter.notify_progress("Test message", 0.5)

    normal_callback.assert_called_once_with("Test message", 0.5)

    assert "Progress callback failed" in caplog.text


@pytest.mark.asyncio
async def test_percentage_bounds(reporter):
    callback = Mock()
    reporter.add_progress_callback(callback)

    # Test minimum value
    await reporter.notify_progress("Start", 0.0)
    callback.assert_called_with("Start", 0.0)

    # Test maximum value
    await reporter.notify_progress("Complete", 1.0)
    callback.assert_called_with("Complete", 1.0)


@pytest.mark.parametrize("message,percentage", [
    ("First step", 0.25),
    ("Halfway there", 0.5),
    ("Almost done", 0.75),
    ("Complete", 1.0)
])
@pytest.mark.asyncio
async def test_various_progress_values(reporter, message, percentage):
    """Test notify_progress with various progress values using parametrize."""
    callback = Mock()
    reporter.add_progress_callback(callback)

    await reporter.notify_progress(message, percentage)
    callback.assert_called_once_with(message, percentage)
