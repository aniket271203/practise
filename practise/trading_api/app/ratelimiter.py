from collections import defaultdict, deque
import threading
import time
from app.config import get_settings
from fastapi import HTTPException, Request

settings=get_settings()

class RateLimiter:
    def __init__(self,requests:int,window_size:int):
        self.max_requests=requests
        self.window_size=window_size
        self.requests=defaultdict(deque)
        self.Locks=defaultdict(threading.Lock)
    
    def is_allowed(self,client_ip:str):
        now=time.perf_counter()
        with self.Locks[client_ip]:
            window=self.requests[client_ip]
            
            while window and now-window[0]>=self.window_size:
                window.popleft()
            
            if len(window)>self.max_requests:
                return False
            window.append(now)
            return True
    
    def get_remaining(self,client_ip:str):
        with self.Locks[client_ip]:
            return max(0,self.max_requests-len(self.requests[client_ip]))
        
rate_limiter=RateLimiter(requests=settings.max_requests_per_min,window_size=60)

def check_rate_limit(request:Request):
    remaining_time=60
    client_ip=request.client.host
    
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="too many requessts",
            headers={'Retry-After':remaining_time}
        )