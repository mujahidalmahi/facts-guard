from functools import lru_cache
import threading

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

from supabase import create_client

from app.config import settings
from app.exceptions import (
    ConfigurationError,
    DatabaseError,
)
from app.logging_config import get_logger

logger = get_logger("dependencies")


class SupabaseService:
    def __init__(
        self,
        url: str,
        api_key: str,
    ):
        if not url or not api_key:
            raise ConfigurationError("Supabase URL and API key are required")

        self.url = url
        self.api_key = api_key
        self._client = None

        self._initialize()

    def _initialize(
        self,
    ) -> None:
        try:
            self._client = create_client(
                self.url,
                self.api_key,
            )

            logger.info("Supabase client initialized successfully")

        except Exception as e:
            raise DatabaseError(f"Failed to initialize Supabase client: {str(e)}")

    def reset_client(self) -> None:
        self._initialize()

    def get_client(
        self,
    ):
        return self._client

    def health_check(
        self,
    ) -> bool:
        try:
            self._client.table("claims").select("id").limit(1).execute()

            return True

        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")

            return False


@lru_cache(maxsize=1)
def get_supabase_service() -> SupabaseService:
    logger.debug("Creating SupabaseService instance")

    return SupabaseService(
        url=settings.SUPABASE_URL,
        api_key=settings.SUPABASE_SERVICE_ROLE_KEY,
    )


def get_supabase_service_instance() -> SupabaseService:
    return get_supabase_service()


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(key: str = Security(api_key_header)):
    if not settings.API_KEYS:
        return key
    valid_keys = set(k for k in settings.API_KEYS.split(",") if k)
    if key not in valid_keys:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
        )
    return key
