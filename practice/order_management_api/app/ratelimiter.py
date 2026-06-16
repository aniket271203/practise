from fastapi import HTTPException, Request
from apis.order_management_api.app.config import get_settings
from collections import defaultdict, deque
import threading
import time

settings=get_settings()

class RateLimiter:
    def __init__(self,max_requests:int,window_size:int):
        self.max_requests=max_requests
        self.window_size=window_size
        self.requests=defaultdict(deque)
        self.locks=defaultdict(threading.Lock)
    
    def is_allowed(self,client_ip:str)->bool:
        now=time.perf_counter()
        with self.locks[client_ip]:
            window=self.requests[client_ip]
            while window and now-window[0]>=self.window_size:
                window.popleft()
            
            if len(window)>self.max_requests:
                return False
            window.append(now)
            return True
    def get_remaining(self,client_ip:str)->int:
        with self.locks[client_ip]:
            return max(0,self.max_requests-len(self.requests[client_ip]))
        
rate_limiter=RateLimiter(max_requests=settings.max_requests_per_min, window_size=60)

async def check_rate_limit(request:Request):
    remaining_time=60
    client_ip=request.client.host
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail=f"Too Many requests | Max {rate_limiter.max_requests} requests allowed in {rate_limiter.window_size} secs",
            headers={"Retry-After":remaining_time}
        )