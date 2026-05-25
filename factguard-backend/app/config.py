from datetime import date
from pathlib import Path
from typing import Optional

from pydantic_settings import (
    BaseSettings,
)


class Settings(
    BaseSettings
):
    APP_NAME: str = (
        "FactGuard API"
    )

    APP_VERSION: str = (
        "1.0.0"
    )

    ENVIRONMENT: str = (
        "development"
    )

    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    FRONTEND_URL: str = (
        "http://localhost:3000"
    )

    CORS_ALLOW_CREDENTIALS: (
        bool
    ) = True

    CORS_ALLOW_METHODS: (
        list[str]
    ) = ["*"]

    CORS_ALLOW_HEADERS: (
        list[str]
    ) = ["*"]

    GEMINI_API_KEYS: str = (
        ""
    )

    GEMINI_MODEL_NAME: str = (
        "gemini-2.5-flash"
    )

    DEEPSEEK_API_KEY: str = (
        ""
    )

    DEEPSEEK_API_KEYS: str = (
        ""
    )

    GROQ_API_KEY: str = (
        ""
    )

    BRIGHTDATA_API_KEY: str = (
        ""
    )

    SUPABASE_URL: (
        Optional[str]
    ) = None

    SUPABASE_SERVICE_ROLE_KEY: (
        Optional[str]
    ) = None

    LOG_LEVEL: str = (
        "INFO"
    )

    LOG_FORMAT: str = (
        "text"
    )

    CLAIM_MIN_LENGTH: int = (
        5
    )

    CLAIM_MAX_LENGTH: int = (
        2000
    )

    CACHE_TTL: int = (
        86400
    )

    REDIS_URL: (
        Optional[str]
    ) = None

    ROUTER_MODEL: str = (
        "gemini-2.5-flash"
    )

    VERIFY_MODEL: str = (
        "gemini-2.5-flash"
    )

    FINANCIAL_MODEL: str = (
        "deepseek/deepseek-v4-flash:free"
    )

    SNIPPET_MAX_CHARS: int = (
        200
    )

    class Config:
        env_file = str(
            Path(
                __file__
            )
            .resolve()
            .parent.parent
            / ".env"
        )

        env_file_encoding = (
            "utf-8"
        )

        case_sensitive = (
            True
        )

        extra = "ignore"

    @property
    def gemini_api_keys_list(
        self,
    ) -> list[str]:
        return [
            key.strip()
            for key in self.GEMINI_API_KEYS.split(
                ","
            )
            if key.strip()
        ]

    @property
    def deepseek_api_keys_list(
        self,
    ) -> list[str]:
        if (
            self.DEEPSEEK_API_KEYS
        ):
            return [
                key.strip()
                for key in self.DEEPSEEK_API_KEYS.split(
                    ","
                )
                if key.strip()
            ]

        if (
            self.DEEPSEEK_API_KEY
        ):
            return [
                self.DEEPSEEK_API_KEY
            ]

        return []

    # NEW dynamic today property
    @property
    def today(self) -> str:
        return (
            date.today()
            .isoformat()
        )

    def validate_required_fields(
        self,
    ) -> None:
        missing = []

        if (
            not self.gemini_api_keys_list
        ):
            missing.append(
                "GEMINI_API_KEYS"
            )

        if (
            not self.SUPABASE_URL
        ):
            missing.append(
                "SUPABASE_URL"
            )

        if (
            not self.SUPABASE_SERVICE_ROLE_KEY
        ):
            missing.append(
                "SUPABASE_SERVICE_ROLE_KEY"
            )

        if missing:
            raise ValueError(
                "Missing required environment variables: "
                + ", ".join(
                    missing
                )
            )


settings = Settings()

# REMOVE CRASH ON IMPORT
# settings.validate_required_fields()