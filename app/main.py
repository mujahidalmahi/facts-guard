"""
FactGuard Backend - Main FastAPI application entry point.
Centralized configuration and middleware setup.
"""

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.schemas import HealthCheckResponse, DetailedHealthCheckResponse
from app.exceptions import FactGuardException
from app.middleware import (
    factguard_exception_handler,
    validation_error_handler,
    general_exception_handler,
)
from app.dependencies import (
    check_database_health,
    check_gemini_health,
)
from app.logging_config import get_logger
from app.api.v1.router import router as api_v1_router

logger = get_logger("main")

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FactGuard - AI-powered misinformation detection system",
)

# Add middleware in order
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add exception handlers
app.add_exception_handler(
    FactGuardException, factguard_exception_handler
)
app.add_exception_handler(
    RequestValidationError, validation_error_handler
)
app.add_exception_handler(Exception, general_exception_handler)

# Include versioned API routers
app.include_router(api_v1_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(
        f"Starting {settings.APP_NAME} v{settings.APP_VERSION} "
        f"in {settings.ENVIRONMENT} mode"
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down FactGuard Backend")


@app.get("/", tags=["system"])
async def root():
    """Root endpoint - welcome message."""
    return {
        "message": "FactGuard Backend running",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["system"])
async def health():
    """Basic health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow().isoformat(),
    )


@app.get(
    "/health/detailed",
    response_model=DetailedHealthCheckResponse,
    tags=["system"],
)
async def health_detailed():
    """Detailed health check including service dependencies."""
    db_healthy = check_database_health()
    gemini_healthy = check_gemini_health()

    overall_status = (
        "healthy"
        if (db_healthy and gemini_healthy)
        else "degraded"
    )

    logger.info(
        f"Health check: database={db_healthy}, gemini={gemini_healthy}"
    )

    return DetailedHealthCheckResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow().isoformat(),
        database="connected" if db_healthy else "disconnected",
        gemini_api="ready" if gemini_healthy else "unavailable",
    )