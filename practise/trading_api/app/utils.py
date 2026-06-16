import time
from functools import wraps
from app.logger import setup_logger

logger=setup_logger(__name__)

def retry(max_attempts:int,delay:float,exception:tuple=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            last_exception=None
            for attempts in range(1,max_attempts+1):
                try:
                    results=func(*args,**kwargs)
                    if attempts>1:
                        logger.debug(f"{func.__name__} succeeded in {attempts} attempts")
                    return results
                except exception as e:
                    last_exception=e
                    logger.debug(f"{func.__name__} failed to run {attempts}/{max_attempts} attempts done")
                    if attempts<max_attempts:
                        time.sleep(delay*attempts)
            logger.warning(f"{func.__name__} failed to run in {max_attempts} attempts")
            raise last_exception
        return wrapper
    return decorator