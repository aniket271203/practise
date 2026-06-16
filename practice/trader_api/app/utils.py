import time
import logging
from functools import wraps

logger=logging.getLogger(__name__)

def retry(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    Retry decorator for unreliable operations like exchange API calls.
    
    Args:
        max_attempts: maximum number of attempts
        delay: seconds to wait between attempts
        exceptions: which exceptions trigger a retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 1:
                        logger.info(f"{func.__name__} succeeded on attempt {attempt}")
                    return result
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"{func.__name__} failed | attempt={attempt}/{max_attempts} | error={str(e)}"
                    )
                    if attempt < max_attempts:
                        time.sleep(delay * attempt)   # exponential backoff
            logger.error(f"{func.__name__} failed after {max_attempts} attempts")
            raise last_exception
        return wrapper
    return decorator