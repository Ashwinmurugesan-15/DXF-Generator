"""
BatchProcessor - Handles concurrent task execution.
Single Responsibility: Thread pool management, fire-and-forget submission.
"""
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List
from dxf_generator.config.env_config import config
from dxf_generator.config.logging_config import logger

class BatchProcessor:
    """
    Manages concurrent task execution using ThreadPoolExecutor.
    Implements fire-and-forget pattern - returns immediately after submission.
    """
   
    def __init__(self, max_workers: int = None):
        self._max_workers = max_workers or config.MAX_THREADS
        self._executor = ThreadPoolExecutor(max_workers=self._max_workers)
        self._submitted_count = 0
    
    def submit(
        self,
        func: Callable,
        *args,
        on_success: Callable = None,
        on_error: Callable = None,
        **kwargs
    ) -> None:
        """
        Submit a task for async execution (fire-and-forget).
        
        Args:
            func: Function to execute
            *args: Positional arguments for func
            on_success: Optional callback on success (receives result)
            on_error: Optional callback on error (receives exception)
            **kwargs: Keyword arguments for func
        """
        future = self._executor.submit(func, *args, **kwargs)
        self._submitted_count += 1
        
        def callback(f):
            exc = f.exception()
            if exc:
                logger.error(f"Task failed: {exc}", exc_info=True)
                if on_error:
                    on_error(exc)
            else:
                if on_success:
                    on_success()
        
        future.add_done_callback(callback)
    
    def submit_batch(
        self,
        tasks: List[tuple],
        on_task_complete: Callable = None,
        on_task_error: Callable = None
    ) -> int:
        """
        Submit multiple tasks for async execution.
        
        Args:
            tasks: List of (func, args, kwargs) tuples
            on_task_complete: Callback for each completed task
            on_task_error: Callback for each failed task
            
        Returns:
            Number of tasks submitted
        """
        
        count = 0
        for task in tasks:
            if len(task) == 1:
                func, args, kwargs = task[0], (), {}
            elif len(task) == 2:
                func, args, kwargs = task[0], task[1], {}
            else:
                func, args, kwargs = task[0], task[1], task[2]
            
            self.submit(
                func,
                *args,
                on_success=on_task_complete,
                on_error=on_task_error,
                **kwargs
            )
            count += 1
        
        logger.info(f"Batch submitted: {count} tasks queued")
        return count
    
    @property
    def submitted_count(self) -> int:
        """Total number of tasks submitted."""
        return self._submitted_count
    
    def shutdown(self, wait: bool = False) -> None:
        """
        Shutdown the executor.
        
        Args:
            wait: If True, wait for pending tasks to complete
        """
        self._executor.shutdown(wait=wait)
        logger.info(f"BatchProcessor shutdown (wait={wait})")


