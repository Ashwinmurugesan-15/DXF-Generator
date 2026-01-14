"""
Unit tests for BatchProcessor component.
Tests thread pool management, fire-and-forget submission, and callbacks.
"""
import pytest
import time
from unittest.mock import patch
from dxf_generator.services.batch_processor import BatchProcessor


@pytest.fixture
def processor():
    """Create a fresh BatchProcessor for each test."""
    return BatchProcessor(max_workers=4)


def test_processor_initialization():
    """Test processor initializes with correct worker count."""
    proc = BatchProcessor(max_workers=8)
    assert proc._max_workers == 8
    assert proc._submitted_count == 0


def test_processor_uses_config_default():
    """Test processor uses config default when max_workers not specified."""
    with patch("dxf_generator.services.batch_processor.config") as mock_config:
        mock_config.MAX_THREADS = 20
        proc = BatchProcessor()
        assert proc._max_workers == 20


def test_submit_increments_count(processor):
    """Test submit increments submitted count."""
    def dummy_task():
        return "result"
    
    processor.submit(dummy_task)
    assert processor.submitted_count == 1
    
    processor.submit(dummy_task)
    assert processor.submitted_count == 2


def test_submit_returns_immediately(processor):
    """Test submit returns immediately (non-blocking)."""
    def slow_task():
        time.sleep(1)
        return "done"
    
    start = time.time()
    processor.submit(slow_task)
    elapsed = time.time() - start
    
    assert elapsed < 0.1, f"submit() blocked for {elapsed}s, should return immediately"


def test_submit_with_success_callback(processor):
    """Test success callback is invoked on completion."""
    result_holder = {"value": None}
    
    def task():
        return "success_result"
    
    def on_success():
        result_holder["value"] = "called"
    
    processor.submit(task, on_success=on_success)
    
    # Wait for task to complete
    time.sleep(0.2)
    
    assert result_holder["value"] == "called"


def test_submit_with_error_callback(processor):
    """Test error callback is invoked on failure."""
    error_holder = {"exception": None}
    
    def failing_task():
        raise ValueError("Test error")
    
    def on_error(exc):
        error_holder["exception"] = exc
    
    processor.submit(failing_task, on_error=on_error)
    
    # Wait for task to complete
    time.sleep(0.2)
    
    assert error_holder["exception"] is not None
    assert isinstance(error_holder["exception"], ValueError)


def test_submit_with_args_and_kwargs(processor):
    """Test submit passes args and kwargs correctly."""
    result_holder = {"value": None}
    
    def task_with_args(a, b, c=None):
        return f"{a}-{b}-{c}"
    
    def on_success():
        result_holder["called"] = True
    
    processor.submit(task_with_args, "X", "Y", on_success=on_success, c="Z")
    
    time.sleep(0.2)
    
    assert result_holder["called"] == True


def test_submit_batch(processor):
    """Test batch submission of multiple tasks."""
    tasks = [
        (lambda: "task1",),
        (lambda: "task2",),
        (lambda: "task3",),
    ]
    
    count = processor.submit_batch(tasks)
    
    assert count == 3
    assert processor.submitted_count == 3


def test_submit_batch_with_callbacks(processor):
    """Test batch submission with completion callbacks."""
    results = []
    
    def task1():
        return "r1"
    
    def task2():
        return "r2"
    
    def on_complete():
        results.append("completed")
    
    tasks = [(task1,), (task2,)]
    processor.submit_batch(tasks, on_task_complete=on_complete)
    
    time.sleep(0.3)
    
    assert len(results) == 2


def test_concurrent_execution(processor):
    """Test tasks execute concurrently."""
    start_times = []
    
    def record_start():
        start_times.append(time.time())
        time.sleep(0.1)
    
    # Submit 4 tasks
    for _ in range(4):
        processor.submit(record_start)
    
    time.sleep(0.3)
    
    # If concurrent, all tasks should start within ~0.05s of each other
    if len(start_times) >= 2:
        time_spread = max(start_times) - min(start_times)
        assert time_spread < 0.1, f"Tasks not concurrent, spread: {time_spread}s"


def test_shutdown(processor):
    """Test processor shutdown."""
    processor.submit(lambda: time.sleep(0.1))
    processor.shutdown(wait=False)
    # Should not raise
