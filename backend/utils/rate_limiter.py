from fastapi import HTTPException, Request, status
import time
from typing import Dict, List

class InMemoryRateLimiter:
    """
    A simple thread-safe(ish) in-memory rate limiter.
    Stores timestamps of requests per IP address.
    """
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Dictionary to store request timestamps: { "ip_address": [ts1, ts2, ...] }
        self.requests: Dict[str, List[float]] = {}

    async def __call__(self, request: Request):
        return await self.check_limit(request)

    async def check_limit(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Cleanup old requests for this IP
        if client_ip in self.requests:
            # Keep only requests within the sliding window
            self.requests[client_ip] = [
                t for t in self.requests[client_ip] 
                if now - t < self.window_seconds
            ]
        else:
            self.requests[client_ip] = []
            
        current_count = len(self.requests[client_ip])
        
        if current_count >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.max_requests} requests per {self.window_seconds} seconds."
            )
            
        # Add current request
        self.requests[client_ip].append(now)

# Instantiate the limiter for generation endpoints
# Limit: 10 requests per 60 seconds
generation_limiter = InMemoryRateLimiter(max_requests=10, window_seconds=60)
