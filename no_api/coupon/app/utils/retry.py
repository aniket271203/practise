import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def retry(max_attempts: int, delay: float, exceptions: tuple = (Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts+1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 1:
                        logger.debug(
                            f"{func.__name__} ran in {attempt} attempts")
                    return result

                except exceptions as e:
                    last_exception = e

                    logger.warning(
                        f"{func.__name__} failed to run trying again {attempt}/{max_attempts} attempt")
                    if attempt < max_attempts:
                        time.sleep(delay*attempt)
            logger.error(f"{func.__name__} failed to run")
            raise (last_exception)
        return wrapper
    return decorator
