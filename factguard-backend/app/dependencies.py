from functools import lru_cache

import google.generativeai as genai
from supabase import create_client

from app.config import settings
from app.exceptions import (
    ConfigurationError,
    DatabaseError,
    GeminiAPIError,
)
from app.logging_config import get_logger

logger = get_logger("dependencies")


class GeminiService:
    def __init__(self, api_keys: list[str], model_name: str):
        if not api_keys:
            raise ConfigurationError("No Gemini API keys provided")

        self.api_keys = api_keys
        self.model_name = model_name
        self._current_key_index = 0
        self._model = None
        self._initialize()

    def _initialize(self) -> None:
        try:
            key = self.api_keys[self._current_key_index]
            genai.configure(api_key=key)
            self._model = genai.GenerativeModel(self.model_name)
            logger.info(f"Gemini API initialized with model: {self.model_name}")
        except Exception as e:
            raise GeminiAPIError(f"Failed to initialize Gemini API: {str(e)}")

    def get_next_key(self) -> str:
        key = self.api_keys[self._current_key_index % len(self.api_keys)]
        self._current_key_index += 1
        return key

    def rotate_key(self) -> None:
        try:
            key = self.get_next_key()
            genai.configure(api_key=key)
            self._model = genai.GenerativeModel(self.model_name)
            logger.info(f"Rotated to next API key (index: {self._current_key_index})")
        except Exception as e:
            raise GeminiAPIError(f"Failed to rotate API key: {str(e)}")

    def get_model(self):
        return self._model


class SupabaseService:
    def __init__(self, url: str, api_key: str):
        if not url or not api_key:
            raise ConfigurationError("Supabase URL and API key are required")

        self.url = url
        self.api_key = api_key
        self._client = None
        self._initialize()

    def _initialize(self) -> None:
        try:
            self._client = create_client(self.url, self.api_key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            raise DatabaseError(f"Failed to initialize Supabase client: {str(e)}")

    def get_client(self):
        return self._client

    def health_check(self) -> bool:
        try:
            self._client.table("claims").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False


@lru_cache(maxsize=1)
def get_gemini_service() -> GeminiService:
    logger.debug("Creating GeminiService instance")
    return GeminiService(
        api_keys=settings.gemini_api_keys_list,
        model_name=settings.GEMINI_MODEL_NAME,
    )


@lru_cache(maxsize=1)
def get_supabase_service() -> SupabaseService:
    logger.debug("Creating SupabaseService instance")
    return SupabaseService(
        url=settings.SUPABASE_URL,
        api_key=settings.SUPABASE_SERVICE_ROLE_KEY,
    )


def get_supabase_service_instance() -> SupabaseService:
    return get_supabase_service()


def get_gemini_service_instance() -> GeminiService:
    return get_gemini_service()
