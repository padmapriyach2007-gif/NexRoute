"""
Pathfinder Backend Scalability & Overload Protection Middleware
Provides per-IP and per-user sliding window rate limiting, request size enforcement,
concurrency bounding, and structured HTTP 429/503 responses to prevent service crashes.
"""

import time
import logging
from typing import Dict, Optional, Tuple, Callable
from collections import deque
import threading
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger("pathfinder.rate_limiter")


class SlidingWindowRateLimiter:
    """Thread-safe sliding-window rate limiter per client identifier."""

    def __init__(self, max_requests_per_window: int = 60, window_seconds: float = 60.0):
        self.max_requests = max_requests_per_window
        self.window_seconds = window_seconds
        self._history: Dict[str, deque] = {}
        self._lock = threading.Lock()

    def is_allowed(self, client_id: str) -> Tuple[bool, int]:
        """
        Returns (is_allowed, retry_after_seconds).
        """
        now = time.time()
        window_start = now - self.window_seconds

        with self._lock:
            if client_id not in self._history:
                self._history[client_id] = deque()

            req_queue = self._history[client_id]

            # Evict expired entries
            while req_queue and req_queue[0] < window_start:
                req_queue.popleft()

            if len(req_queue) >= self.max_requests:
                oldest = req_queue[0]
                retry_after = max(1, int(oldest + self.window_seconds - now))
                return False, retry_after

            req_queue.append(now)
            return True, 0

    def clean_stale(self, max_idle_seconds: float = 300.0):
        """Cleans up idle client tracking to prevent unbounded memory growth."""
        now = time.time()
        with self._lock:
            stale_keys = [
                k for k, q in self._history.items()
                if not q or (now - q[-1] > max_idle_seconds)
            ]
            for k in stale_keys:
                del self._history[k]


class ScalabilityProtectionMiddleware(BaseHTTPMiddleware):
    """
    FastAPI / Starlette middleware enforcing:
    1. Maximum request body size (prevents memory exhaustion)
    2. Per-client sliding window rate limits
    3. Global concurrency limits
    4. Structured JSON error responses
    """

    def __init__(
        self,
        app,
        max_request_bytes: int = 2 * 1024 * 1024,      # 2 MB
        general_rate_limit: int = 120,                  # 120 req/min
        strict_rate_limit: int = 25,                    # 25 req/min for expensive AI / Route endpoints
        max_concurrent_requests: int = 64
    ):
        super().__init__(app)
        self.max_request_bytes = max_request_bytes
        self.general_limiter = SlidingWindowRateLimiter(general_rate_limit, 60.0)
        self.strict_limiter = SlidingWindowRateLimiter(strict_rate_limit, 60.0)
        self._concurrency_semaphore = threading.BoundedSemaphore(max_concurrent_requests)
        self._active_requests = 0
        self._lock = threading.Lock()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract client IP
        forwarded = request.headers.get("x-forwarded-for")
        client_ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "127.0.0.1")
        path = request.url.path

        # Health checks bypass rate limiting to prevent false negatives in load balancers
        if path.startswith("/health") or path.startswith("/api/health"):
            return await call_next(request)

        # 1. Enforce Request Content-Length Size Limit
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.max_request_bytes:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "PAYLOAD_TOO_LARGE",
                            "message": f"Request body exceeds maximum allowed size ({self.max_request_bytes // 1024 // 1024} MB)."
                        }
                    )
            except ValueError:
                pass

        # 2. Enforce Rate Limiting
        is_expensive_route = any(path.startswith(p) for p in ["/api/route", "/api/v2/routes", "/api/v2/ai-planner", "/api/geocode"])
        limiter = self.strict_limiter if is_expensive_route else self.general_limiter
        allowed, retry_after = limiter.is_allowed(client_ip)

        if not allowed:
            return JSONResponse(
                status_code=429,
                headers={"Retry-After": str(retry_after)},
                content={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": f"Too many requests from client {client_ip}. Please retry after {retry_after} seconds.",
                    "retry_after_seconds": retry_after
                }
            )

        # 3. Enforce Concurrency Bound
        acquired = self._concurrency_semaphore.acquire(blocking=False)
        if not acquired:
            return JSONResponse(
                status_code=503,
                headers={"Retry-After": "2"},
                content={
                    "error": "SERVER_OVERLOADED",
                    "message": "The server is currently operating at maximum concurrent capacity. Please retry shortly.",
                    "retry_after_seconds": 2
                }
            )

        try:
            with self._lock:
                self._active_requests += 1

            start_t = time.time()
            response = await call_next(request)
            duration_ms = round((time.time() - start_t) * 1000, 2)
            response.headers["X-Response-Time-Ms"] = str(duration_ms)
            return response

        except Exception as e:
            logger.error(f"Unhandled server exception on {path}: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred while processing the request."
                }
            )
        finally:
            with self._lock:
                self._active_requests = max(0, self._active_requests - 1)
            self._concurrency_semaphore.release()
