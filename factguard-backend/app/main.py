from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.api.history import router as history_router
from app.api.verify import router as verify_router
from app.config import settings
from app.exceptions import FactGuardException
from app.logging_config import get_logger
from app.middleware import (
    factguard_exception_handler,
    general_exception_handler,
    validation_error_handler,
)

logger = get_logger("main")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

app.add_exception_handler(FactGuardException, factguard_exception_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(verify_router)
app.include_router(history_router)


@app.get("/")
async def root():
    return {"message": "FactGuard backend running"}


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION, "environment": settings.ENVIRONMENT}
