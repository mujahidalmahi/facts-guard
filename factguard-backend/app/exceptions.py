from typing import Any

from app.utils.constants import (
    ERROR_ANALYSIS_FAILED,
    ERROR_CLAIM_NOT_FOUND,
    ERROR_CONFIG,
    ERROR_DATABASE,
    ERROR_GEMINI_API,
    ERROR_INTERNAL,
    ERROR_VALIDATION,
)


class FactGuardException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = ERROR_INTERNAL,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(FactGuardException):
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code=ERROR_VALIDATION,
            details=details,
        )


class ClaimNotFoundError(FactGuardException):
    def __init__(self, job_id: str):
        super().__init__(
            message=f"Result not found for job ID: {job_id}",
            status_code=404,
            error_code=ERROR_CLAIM_NOT_FOUND,
            details={"job_id": job_id},
        )


class AnalysisFailedError(FactGuardException):
    def __init__(self, reason: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=f"Analysis failed: {reason}",
            status_code=500,
            error_code=ERROR_ANALYSIS_FAILED,
            details=details or {"reason": reason},
        )


class GeminiAPIError(FactGuardException):
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=f"Gemini API error: {message}",
            status_code=503,
            error_code=ERROR_GEMINI_API,
            details=details,
        )


class DatabaseError(FactGuardException):
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=f"Database error: {message}",
            status_code=500,
            error_code=ERROR_DATABASE,
            details=details,
        )


class ConfigurationError(FactGuardException):
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=f"Configuration error: {message}",
            status_code=500,
            error_code=ERROR_CONFIG,
            details=details,
        )
