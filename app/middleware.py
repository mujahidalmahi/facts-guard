"""
Exception handling middleware for FactGuard backend.
Converts custom exceptions to proper HTTP responses.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import traceback

from app.exceptions import FactGuardException
from app.logging_config import get_logger

logger = get_logger("exception_handler")


async def factguard_exception_handler(
    request: Request, exc: FactGuardException
):
    """Handle FactGuard custom exceptions."""
    logger.warning(
        f"FactGuard exception: {exc.error_code}",
        error_code=exc.error_code,
        status_code=exc.status_code,
        message=exc.message,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        },
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
):
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(x) for x in error["loc"][1:]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    logger.warning(
        f"Validation error on {request.url.path}",
        validation_errors=errors,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {"errors": errors},
        },
    )


async def general_exception_handler(
    request: Request, exc: Exception
):
    """Handle unexpected exceptions."""
    logger.error(
        f"Unexpected error on {request.url.path}",
        error_type=type(exc).__name__,
        error_message=str(exc),
        traceback=traceback.format_exc(),
        path=request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": {
                "error_type": type(exc).__name__,
            },
        },
    )
