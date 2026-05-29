from datetime import date
from pathlib import Path
from typing import Optional

from pydantic_settings import (
    BaseSettings,
)


class Settings(BaseSettings):
    APP_NAME: str = "FactGuard API"

    APP_VERSION: str = "1.0.0"

    ENVIRONMENT: str = "development"

    DEBUG: bool = False

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    FRONTEND_URL: str = "http://localhost:3000"

    CORS_ALLOW_CREDENTIALS: bool = True

    CORS_ALLOW_METHODS: list[str] = ["*"]

    CORS_ALLOW_HEADERS: list[str] = ["*"]

    BRIGHTDATA_API_KEY: str = ""

    BRIGHTDATA_SERP_ZONE: str = ""

    BRIGHTDATA_BROWSER_ZONE: str = ""

    BRIGHTDATA_WSS: str = ""

    BROWSER_TIMEOUT: int = 45

    MAX_BROWSER_PAGES: int = 1

    CACHE_TTL_BROWSER: int = 3600

    SUPABASE_URL: Optional[str] = None

    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None

    LOG_LEVEL: str = "INFO"

    LOG_FORMAT: str = "text"

    CLAIM_MIN_LENGTH: int = 5

    CLAIM_MAX_LENGTH: int = 2000

    API_KEYS: str = ""

    CACHE_TTL: int = 86400

    REDIS_URL: Optional[str] = None

    SNIPPET_MAX_CHARS: int = 200

    AIML_API_KEYS: str = ""

    AIML_API_MODEL: str = "openai/gpt-5-2-chat-latest"

    AIML_API_ENABLED: bool = True

    AIML_VERIFY_MODEL: str = "openai/gpt-5-2-chat-latest"

    AIML_FINANCIAL_MODEL: str = "openai/gpt-5-2-chat-latest"

    AIML_ROUTER_MODEL: str = "openai/gpt-4.1-nano-2025-04-14"

    AIML_CART_MODEL: str = "openai/gpt-4o-mini"

    @property
    def aiml_api_keys_list(self) -> list[str]:
        return [k.strip() for k in self.AIML_API_KEYS.split(",") if k.strip()]

    class Config:
        env_file = str(Path(__file__).resolve().parent.parent / ".env")

        env_file_encoding = "utf-8"

        case_sensitive = True

        extra = "ignore"

    # NEW dynamic today property
    @property
    def today(self) -> str:
        return date.today().isoformat()

    def validate_required_fields(
        self,
    ) -> None:
        missing = []

        if not self.REDIS_URL:
            missing.append("REDIS_URL")

        if not self.SUPABASE_URL:
            missing.append("SUPABASE_URL")

        if missing and self.ENVIRONMENT == "production":
            raise RuntimeError("Missing required environment variables: " + ", ".join(missing))

        if missing:
            import logging

            logging.warning(f"Missing optional env vars (fatal in production): {missing}")


settings = Settings()

# REMOVE CRASH ON IMPORT
# settings.validate_required_fields()
