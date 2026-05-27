import hashlib
import asyncio

from app.config import settings
from app.logging_config import get_logger
from app.services.cache import _get_client

logger = get_logger("browser_cache")


def _url_cache_key(url: str) -> str:
    return f"factguard:browser_extract:" f"{hashlib.sha256(url.encode('utf-8')).hexdigest()}"


async def get_cached_browser_extract(
    url: str,
) -> str | None:
    try:
        client = _get_client()
        if client is None:
            return None
        data = await asyncio.to_thread(
            client.get,
            _url_cache_key(url),
        )
        return data if data else None
    except Exception as e:
        logger.warning(f"Redis get_browser_extract failed: {e}")
        return None


async def set_cached_browser_extract(
    url: str,
    text: str,
) -> None:
    try:
        client = _get_client()
        if client is None:
            return
        await asyncio.to_thread(
            client.setex,
            _url_cache_key(url),
            settings.CACHE_TTL_BROWSER,
            text,
        )
    except Exception as e:
        logger.warning(f"Redis set_browser_extract failed: {e}")
