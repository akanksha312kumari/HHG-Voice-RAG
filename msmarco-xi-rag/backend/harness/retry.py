"""Retry utilities for offline/background tasks."""

def with_retry():
    """
    Retry decorator for offline indexing, deployment/background operations, 
    and non-critical operations only. Do not use for blocking interactive retries.
    """
    # TODO: Implement retry logic using tenacity
    pass
