"""
Redis-backed sliding window rate limiter middleware.
Limits requests per IP. Auth and submit endpoints have tighter limits
(those are also limited at Nginx level, this is the backend defence-in-depth).
"""

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config      import settings
from app.core.redis_client import get_redis


# Per-route overrides  { path_prefix: (requests, window_seconds) }
ROUTE_LIMITS = {
    "/api/auth/login":    (settings.MAX_LOGIN_ATTEMPTS * 2, 60),
    "/api/auth/register": (10, 60),
    "/api/challenges/submit": (settings.ANSWER_SUBMIT_LIMIT, 60),
}
DEFAULT_LIMIT  = (settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_WINDOW)


class RateLimitMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        # Health check and static assets bypass rate limiting
        path = request.url.path
        if path in ("/health", "/") or path.startswith("/static"):
            return await call_next(request)

        ip    = self._get_ip(request)
        limit, window = self._get_limit(path)
        key   = f"rl:{ip}:{path}:{int(time.time()) // window}"

        try:
            redis = await get_redis()
            pipe  = redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, window)
            results = await pipe.execute()
            count = results[0]
        except Exception:
            # If Redis is down, fail open (don't block traffic)
            return await call_next(request)

        if count > limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
                headers={
                    "Retry-After": str(window),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"]     = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - count))
        return response

    @staticmethod
    def _get_ip(request: Request) -> str:
        """Extract real IP, respecting X-Forwarded-For from trusted proxy."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    @staticmethod
    def _get_limit(path: str):
        for prefix, limits in ROUTE_LIMITS.items():
            if path.startswith(prefix):
                return limits
        return DEFAULT_LIMIT
