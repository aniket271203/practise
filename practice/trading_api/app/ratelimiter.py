import time
from collections import defaultdict, deque
import threading
from fastapi import Request, HTTPException
from apis.trading_api.app.config import get_settings

settings=get_settings()


class RateLImiter:
    def __init__(self, max_requests: int = 10, window_size: int = 60):
        self.max_requests = max_requests
        self.window_size = window_size
        self.requests = defaultdict(deque)
        self.locks = defaultdict(threading.Lock)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.perf_counter()
        with self.locks[client_ip]:
            window = self.requests[client_ip]

            if window and now-window[0] >= self.window_size:
                window.popleft()

            if len(window) >= self.max_requests:
                return False
            window.append(now)
            return True

    def get_remaining(self, client_ip: str) -> int:
        with self.locks[client_ip]:
            return max(0, self.max_requests-len(self.requests[client_ip]))


rate_limiter = RateLImiter(max_requests=settings.max_requests_per_minute, window_size=60)

# can use this function to use rate limiting in the API


def check_rate_limit(request: Request):
    remaining_time = 60
    client_ip = request.client.host
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429,
                            detail=f"too many request from the client, Max {rate_limiter.max_requests} requests allowed in {rate_limiter.window_size}",
                            headers={"Retry-After": str(remaining_time)})
