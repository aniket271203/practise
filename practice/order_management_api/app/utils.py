import time
import logging
from functools import wraps

logger=logging.getLogger(__name__)

def retry(max_attempts:int=3, delay:float=1.0,exceptions:tuple=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception=None
            for attempts in range(1,max_attempts=1):
                try:
                    result=func(*args, **kwargs)
                    if attempts>1:
                        logger.info(f"{func.__name__} sucessfuly ran in {attempts}/{max_attempts} attempts")
                    
                    return result
                except exceptions as e:
                    last_exception=e
                    logger.warning(f"{func.__name__} failed to run | {max_attempts-attempts}/{max_attempts} remaining")
                    if attempts<max_attempts:
                        time.sleep(delay*attempts)
            logger.warning(f"{func.__name__} failed to run")
            raise last_exception
        return wrapper
    return decorator