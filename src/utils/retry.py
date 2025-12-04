"""Retry utilities for API calls"""

import logging
import time
from typing import Callable, TypeVar, Optional, List
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_on_failure(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator for retrying function calls on failure
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Optional callback function called on each retry
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        if on_retry:
                            try:
                                on_retry(attempt, e)
                            except Exception as callback_error:
                                logger.error(f"Retry callback failed: {callback_error}")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
            
            return None
        
        return wrapper
    return decorator


def safe_api_call(
    func: Callable[..., T],
    default: Optional[T] = None,
    log_error: bool = True
) -> Optional[T]:
    """
    Safely call an API function with error handling
    
    Args:
        func: Function to call
        default: Default value to return on failure
        log_error: Whether to log errors
    
    Returns:
        Function result or default value
    """
    try:
        return func()
    except Exception as e:
        if log_error:
            logger.error(f"API call failed: {e}")
        return default

