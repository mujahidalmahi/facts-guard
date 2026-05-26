import os

from contextlib import (
    asynccontextmanager,
)

from fastapi import (
    FastAPI,
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

from app.config import (
    settings,
)

from app.exceptions import (
    FactGuardException,
)

from app.logging_config import (
    get_logger,
)

from app.middleware import (
    factguard_exception_handler,
    general_exception_handler,
    validation_error_handler,
)
from app.middleware.audit import AuditMiddleware
from app.middleware.ratelimit import RateLimitMiddleware
from app.services.routing import health_check as routing_health

logger = get_logger(
    "main"
)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    try:
        settings.validate_required_fields()
        logger.info("All required env vars present")
    except ValueError as e:
        logger.error(f"Config warning: {e}")

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    os.getenv("FRONTEND_URL", ""),
    "https://*.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in ALLOWED_ORIGINS if o],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    verify_router
)

app.include_router(
    pricing_router
)

app.include_router(
    financial_router
)

app.include_router(
    history_router
)

app.include_router(
    threats_router
)


@app.get("/")
async def root():
    return {
        "message":
            "FactGuard backend running"
    }


@app.get("/health")
async def health():
    cb_status = await routing_health()
    return {
        "status":
            "ok",
        "version":
            settings.APP_VERSION,
        "environment":
            settings.ENVIRONMENT,
        "circuit_breakers": cb_status,
    }

@app.get("/routing/health")
async def routing_status():
    return await routing_health()