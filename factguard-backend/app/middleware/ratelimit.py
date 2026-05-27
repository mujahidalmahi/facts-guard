import redis.asyncio as aioredis
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings
from app.logging_config import get_logger

logger = get_logger("ratelimit")


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 30, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._redis = aioredis.from_url(settings.REDIS_URL) if settings.REDIS_URL else None

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/health"):
            return await call_next(request)

        if self._redis is None:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"rl:{client_ip}"

        try:
            count = await self._redis.incr(key)
            if count == 1:
                await self._redis.expire(key, self.window_seconds)

            if count > self.max_requests:
                logger.warning(f"Rate limit exceeded for {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please try again later."},
                )
        except Exception as e:
            logger.warning(f"Rate limit check failed: {e}")

        return await call_next(request)
