"""
Custom exception classes for FactGuard backend.
Provides consistent error handling across the application.
"""

from fastapi import HTTPException
from typing import Any


class FactGuardException(Exception):
    """Base exception for all FactGuard errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(FactGuardException):
    """Raised when input validation fails."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class ClaimNotFoundError(FactGuardException):
    """Raised when a claim/result is not found."""

    def __init__(self, job_id: str):
        super().__init__(
            message=f"Result not found for job ID: {job_id}",
            status_code=404,
            error_code="CLAIM_NOT_FOUND",
            details={"job_id": job_id},
        )


class AnalysisFailedError(FactGuardException):
    """Raised when claim analysis fails."""

    def __init__(self, reason: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=f"Analysis failed: {reason}",
            status_code=500,
            error_code="ANALYSIS_FAILED",
            details=details or {"reason": reason},
        )


class GeminiAPIError(FactGuardException):
    """Raised when Gemini API call fails."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=f"Gemini API error: {message}",
            status_code=503,
            error_code="GEMINI_API_ERROR",
            details=details,
        )


class DatabaseError(FactGuardException):
    """Raised when database operations fail."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=f"Database error: {message}",
            status_code=500,
            error_code="DATABASE_ERROR",
            details=details,
        )


class ConfigurationError(FactGuardException):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=f"Configuration error: {message}",
            status_code=500,
            error_code="CONFIGURATION_ERROR",
            details=details,
        )


def convert_to_http_exception(exc: FactGuardException) -> HTTPException:
    """Convert FactGuardException to FastAPI HTTPException."""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        },
    )
