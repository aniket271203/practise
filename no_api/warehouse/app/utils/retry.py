import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def retry(max_attempts: int, delay: float, exceptions: tuple = (Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_attempts+1):
                try:
                    results = func(*args, **kwargs)
                    if attempt > 1:
                        logger.debug(
                            f"{func.__name__} ran succesfully in {attempt}/{max_attempts} attempts")
                    return results
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"{func.__name__} failed to run {max_attempts-attempt} attempts left")
                    if attempt < max_attempts:
                        time.sleep(delay*attempt)

            logger.error(
                f"{func.__name__} failed to run all attempts exhausted")
            raise last_exception
        return wrapper
    return decorator
