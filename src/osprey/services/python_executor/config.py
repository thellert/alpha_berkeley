"""
Python Executor Configuration Module

This module contains configuration classes for the Python executor service.
Separated from service.py to avoid circular import issues.
"""

from typing import Any


class PythonExecutorConfig:
    """Configuration for Python Executor Service.

    Manages essential configuration settings for the Python executor service,
    including retry limits and execution timeouts. Values can be overridden
    via framework configuration.
    """

    def __init__(self, configurable: dict[str, Any] = None):
        config = configurable or {}
        executor_config = config.get("python_executor", {})

        # Retry configuration - how many times to retry failed operations
        self.max_generation_retries = executor_config.get("max_generation_retries", 3)
        self.max_execution_retries = executor_config.get("max_execution_retries", 3)

        # Timeout configuration - how long to wait for operations
        self.execution_timeout_seconds = executor_config.get("execution_timeout_seconds", 600)  # 10 minutes
