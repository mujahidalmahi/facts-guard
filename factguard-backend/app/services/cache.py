import asyncio
import hashlib
import json
import os
from pathlib import Path

import redis
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

CACHE_TTL = int(os.getenv("CACHE_TTL", "86400"))
REDIS_URL = os.getenv("REDIS_URL")

_redis_client = None


def _get_client():
    global _redis_client
    if _redis_client is None and REDIS_URL:
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
    except Exception:
        return None


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
    except Exception:
        pass
