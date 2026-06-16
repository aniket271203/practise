import time
from functools import wraps
import logging

logger=logging.getLogger(__name__)

def retry(max_attempts:int,delay:float,exceptions:tuple=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            last_exception=None
            
            for attempts in range(1,max_attempts+1):
                try:
                    
                    result=func(*args,**kwargs)
                    if attempts>1:
                        logger.debug(f"{func.__name__} ran in {attempts} attempts")
                    return result
                except exceptions as e:
                    last_exception=e
                    logger.warning(f"{func.__name__} failed to run | {max_attempts-attempts} attempts left")
                    if attempts<max_attempts:
                        time.sleep(delay*attempts)
            logger.error(f"{func.__name__} failed to run all attempts exhausted")
            raise last_exception
        return wrapper
    return decorator