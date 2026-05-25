import asyncio
import hashlib
import json
import threading

import redis

from app.config import settings
from app.logging_config import get_logger

logger = get_logger("cache")

CACHE_TTL = settings.CACHE_TTL
REDIS_URL = settings.REDIS_URL

_redis_client = None
_redis_lock = threading.Lock()


def _get_client():
    global _redis_client
    if _redis_client is None and REDIS_URL:
        with _redis_lock:
            if _redis_client is None:
                _redis_client = redis.Redis.from_url(
                    REDIS_URL, decode_responses=True
                )
    return _redis_client


def compute_claim_hash(claim: str) -> str:
    normalized = claim.strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


async def get_cached_analysis(claim_hash: str) -> dict | None:
    try:
        client = _get_client()
        if client is None:
            return None
        data = await asyncio.to_thread(
            client.get, f"factguard:claim:{claim_hash}"
        )
        return json.loads(data) if data else None
    except Exception as e:
        logger.warning(f"Redis get_cached_analysis failed: {str(e)}")
        return None


async def set_progress(job_id: str, step: str) -> None:
    try:
        client = _get_client()
        if client is None:
            return
        await asyncio.to_thread(
            client.setex, f"factguard:progress:{job_id}", 300, step
        )
    except Exception:
        pass


async def get_progress(job_id: str) -> str | None:
    try:
        client = _get_client()
        if client is None:
            return None
        data = await asyncio.to_thread(
            client.get, f"factguard:progress:{job_id}"
        )
        return data if data else None
    except Exception:
        return None


HISTORY_CACHE_KEY = "factguard:history:claims"
HISTORY_CACHE_LIMIT = 50


async def get_cached_history() -> list[dict] | None:
    try:
        client = _get_client()
        if client is None:
            return None
        data = await asyncio.to_thread(
            client.lrange, HISTORY_CACHE_KEY, 0, -1
        )
        return [json.loads(item) for item in data] if data else []
    except Exception as e:
        logger.warning(f"Redis get_cached_history failed: {str(e)}")
        return None


async def push_claim_to_history(claim_data: dict) -> None:
    try:
        client = _get_client()
        if client is None:
            return
        pipe = client.pipeline()
        pipe.lpush(HISTORY_CACHE_KEY, json.dumps(claim_data))
        pipe.ltrim(HISTORY_CACHE_KEY, 0, HISTORY_CACHE_LIMIT - 1)
        await asyncio.to_thread(pipe.execute)
    except Exception as e:
        logger.warning(f"Redis push_claim_to_history failed: {str(e)}")


async def set_cached_analysis(claim_hash: str, data: dict) -> None:
    try:
        client = _get_client()
        if client is None:
            return
        await asyncio.to_thread(
            client.setex,
            f"factguard:claim:{claim_hash}",
            CACHE_TTL,
            json.dumps(data),
        )
    except Exception as e:
        logger.warning(f"Redis set_cached_analysis failed: {str(e)}")


async def set_job_query(job_id: str, query: str) -> None:
    try:
        client = _get_client()
        if client is None:
            return
        await asyncio.to_thread(
            client.setex,
            f"factguard:query:{job_id}",
            86400,
            query,
        )
    except Exception as e:
        logger.warning(f"Redis set_job_query failed: {str(e)}")


async def get_job_query(job_id: str) -> str | None:
    try:
        client = _get_client()
        if client is None:
            return None
        data = await asyncio.to_thread(
            client.get, f"factguard:query:{job_id}"
        )
        return data if data else None
    except Exception as e:
        logger.warning(f"Redis get_job_query failed: {str(e)}")
        return None


async def set_job_result(job_id: str, data: dict) -> None:
    try:
        client = _get_client()
        if client is None:
            return
        await asyncio.to_thread(
            client.setex,
            f"factguard:job_result:{job_id}",
            86400,
            json.dumps(data),
        )
    except Exception as e:
        logger.warning(f"Redis set_job_result failed: {str(e)}")


async def get_job_result(job_id: str) -> dict | None:
    try:
        client = _get_client()
        if client is None:
            return None
        data = await asyncio.to_thread(
            client.get, f"factguard:job_result:{job_id}"
        )
        return json.loads(data) if data else None
    except Exception as e:
        logger.warning(f"Redis get_job_result failed: {str(e)}")
        return None
