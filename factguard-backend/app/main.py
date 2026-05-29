import os
import sys
import asyncio
import uuid

os.environ.setdefault("NO_COLOR", "1")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from contextlib import (
    asynccontextmanager,
)

from fastapi import (
    Depends,
    FastAPI,
)

from app.dependencies import (
    require_api_key,
)
from fastapi.exceptions import (
    RequestValidationError,
)
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.api.history import (
    router as history_router,
)

from app.api.pricing import (
    router as pricing_router,
)

from app.api.verify import (
    router as verify_router,
)

from app.api.financial import (
    router as financial_router,
)

from app.api.threats import (
    router as threats_router,
)

from app.api.metrics import (
    router as metrics_router,
)

from app.config import (
    settings,
)

from app.exceptions import (
    FactGuardException,
)

from app.logging_config import (
    get_logger,
    request_id_ctx,
)

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.middleware import (
    factguard_exception_handler,
    general_exception_handler,
    validation_error_handler,
)
from app.middleware.audit import AuditMiddleware
from app.middleware.ratelimit import RateLimitMiddleware
from app.services.routing import health_check as routing_health

logger = get_logger("main")


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    try:
        settings.validate_required_fields()
        logger.info("All required env vars present")
    except (ValueError, RuntimeError) as e:
        logger.error(f"Config error: {e}")
        if settings.ENVIRONMENT == "production":
            raise

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    settings.FRONTEND_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in ALLOWED_ORIGINS if o],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        token = request_id_ctx.set(rid)
        try:
            return await call_next(request)
        finally:
            request_id_ctx.reset(token)


app.add_middleware(RequestIDMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=30, window_seconds=60)

app.add_exception_handler(
    FactGuardException,
    factguard_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_error_handler,
)

app.add_exception_handler(
    Exception,
    general_exception_handler,
)

# Routers
app.include_router(
    verify_router,
    dependencies=[Depends(require_api_key)],
)

app.include_router(
    pricing_router,
    dependencies=[Depends(require_api_key)],
)

app.include_router(
    financial_router,
    dependencies=[Depends(require_api_key)],
)

app.include_router(
    history_router,
    dependencies=[Depends(require_api_key)],
)

app.include_router(
    threats_router,
    dependencies=[Depends(require_api_key)],
)

app.include_router(
    metrics_router,
)


@app.get("/")
async def root():
    return {"message": "FactGuard backend running"}


@app.get("/health")
async def health():
    cb_status = await routing_health()
    aiml_status = {}
    if settings.AIML_API_ENABLED and settings.aiml_api_keys_list:
        from app.services.aiml_service import get_aiml_key_status
        aiml_status = await get_aiml_key_status()
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "circuit_breakers": cb_status,
        "aiml_keys": aiml_status,
    }


@app.get("/routing/health")
async def routing_status():
    return await routing_health()
