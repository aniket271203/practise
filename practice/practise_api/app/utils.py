import time
import logging
from functools import wraps

logger=logging.getLogger(__name__)

def retry(max_attempts:int,delay:float,exception:tuple=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            last_exception=None
            for attempts in range(1,max_attempts+1):
                try:
                    result=func(*args,**kwargs)

                    if attempts>1:
                        logger.warning(f"{func.__name__} successfully ran in {attempts} attempts")
                    return result
                except Exception as e:
                    last_exception=e
                    logger.warning(f"{func.__name__} failed to run | {attempts}/{max_attempts} completed")
                    if attempts<max_attempts:
                        time.sleep(delay*attempts)
                
            logger.error(f"{func.__name__} failed to run after {max_attempts} attempts")
            raise last_exception
        return wrapper
    return decorator

