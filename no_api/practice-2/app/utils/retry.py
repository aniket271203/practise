import time
from functools import wraps
import logging

logger=logging.getLogger(__name__)

def retry(max_attempts:int=3,delay:float=1.0,exceptions:tuple=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            last_exception=None
            for attempts in range(1,max_attempts+1):
                try:
                    results=func(*args,**kwargs)
                    if attempts>1:
                        logger.debug(f"{func.__name__} ran in {attempts} attempts")
                    return results
                except exceptions as e:
                    last_exception=e
                    logger.debug(f"{func.__name__} failed to run | {attempts}/{max_attempts} attempts done")
                    if attempts<max_attempts:
                        time.sleep(delay*attempts)
            logger.error(f"{func.__name__} failed to run all attempts exhausted")
            raise last_exception
        return wrapper
    return decorator
