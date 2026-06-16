from fastapi import HTTPException
from functools import wraps
import time 
import logging

logger=logging.getLogger(__name__)

def retry(max_attempts:int=3, delay:float=1.0, exceptions:tuple=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            last_exception=None
            for attempts in range(1,max_attempts+1):
                try:
                    result=func(*args,**kwargs)
                    if attempts>1:
                        logger.info(f"{func.__name__} succeeded on {attempts} attempts")
                    return result
                except Exception as e:
                    last_exception=e
                    logger.warning(f"{func.__name__} failed to run, {attempts}/{max_attempts} attempts done")
                    if attempts<=max_attempts:
                        time.sleep(delay*attempts)        
            logger.error(f"Func Failed to run after {max_attempts} attempts")
            raise last_exception
        return wrapper
    return decorator
