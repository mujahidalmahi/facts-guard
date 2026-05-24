"""
Centralized configuration management for FactGuard backend.
Uses Pydantic BaseSettings for validation and type safety.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Configuration
    APP_NAME: str = "FactGuard API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS Configuration
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # Google Gemini API Configuration
    GEMINI_API_KEYS: str  # Comma-separated list of API keys
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"

    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" or "text"

    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 10
    RATE_LIMIT_PERIOD: int = 60  # seconds

    # Validation Configuration
    CLAIM_MIN_LENGTH: int = 5
    CLAIM_MAX_LENGTH: int = 2000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def gemini_api_keys_list(self) -> list[str]:
        """Parse comma-separated API keys into a list."""
        return [
            key.strip()
            for key in self.GEMINI_API_KEYS.split(",")
            if key.strip()
        ]

    def validate_required_fields(self) -> None:
        """Validate that all required fields are set."""
        required_fields = {
            "GEMINI_API_KEYS": "Google Gemini API keys",
            "SUPABASE_URL": "Supabase project URL",
            "SUPABASE_SERVICE_ROLE_KEY": "Supabase service role key",
        }

        missing_fields = []
        for field, description in required_fields.items():
            value = getattr(self, field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_fields.append(f"{field} ({description})")

        if missing_fields:
            raise ValueError(
                f"Missing required environment variables:\n"
                + "\n".join(f"  - {field}" for field in missing_fields)
            )


# Create global settings instance
try:
    settings = Settings()
    settings.validate_required_fields()
except ValueError as e:
    print(f"Configuration Error: {e}")
    raise
