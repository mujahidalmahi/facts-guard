import asyncio
import time
from typing import Any, Callable

import redis.asyncio as aioredis

from app.config import settings
from app.logging_config import get_logger
from app.services.brightdata import (
    crawl_extract,
    unlocker_scrape,
    browser_render,
    serp_search,
    mcp_discover,
)
from app.services.cache import get_cached_serp, set_cached_serp
from app.utils.duckduckgo import search as _duckduckgo_search

logger = get_logger("routing")


_redis_client: aioredis.Redis | None = None
_cb_failures: dict[str, list[float]] = {}


async def _get_redis() -> aioredis.Redis | None:
    global _redis_client
    if _redis_client is None and settings.REDIS_URL:
        _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def _call_with_circuit_breaker(
    name: str,
    func: Callable,
    *args,
    threshold: int = 3,
    cooldown: float = 30.0,
) -> Any:
    client = await _get_redis()

    if client is not None:
        cb_key = f"cb:{name}"
        failures = int(await client.hget(cb_key, "failures") or 0)
        last_fail = float(await client.hget(cb_key, "last") or 0)
        is_open = failures >= threshold

        if is_open and (time.time() - last_fail > cooldown):
            await client.hset(cb_key, "failures", 0)
            is_open = False

        if is_open:
            logger.warning(f"Circuit breaker '{name}' is OPEN — skipping")
            return None

        try:
            result = await func(*args)
            if result is not None and result != []:
                await client.hset(cb_key, "failures", 0)
                return result
            raise ValueError(f"Empty result from {name}")
        except Exception as e:
            await client.hincrby(cb_key, "failures", 1)
            await client.hset(cb_key, "last", time.time())
            await client.expire(cb_key, int(cooldown * 10))
            new_failures = int(await client.hget(cb_key, "failures") or 0)
            logger.warning(f"Circuit breaker '{name}' failure {new_failures}/{threshold}: {e}")
            return None

    cb_state = _cb_failures.get(name, [])
    now = time.time()
    cb_state = [t for t in cb_state if now - t < cooldown]
    if len(cb_state) >= threshold:
        logger.warning(f"Circuit breaker '{name}' is OPEN (fallback) — skipping")
        return None

    try:
        result = await func(*args)
        if result is not None and result != []:
            _cb_failures[name] = []
            return result
        raise ValueError(f"Empty result from {name}")
    except Exception as e:
        cb_state.append(now)
        _cb_failures[name] = cb_state
        logger.warning(f"Circuit breaker '{name}' failure {len(cb_state)}/{threshold}: {e}")
        return None


async def extract_article_content(url: str) -> dict:
    """Three-tier fallback for article extraction with Bright Data product labels."""
    result = {}

    result = await _call_with_circuit_breaker(
        "crawl_api", crawl_extract, url, threshold=2, cooldown=15.0
    )
    if result:
        result["tier"] = 1
        result["bright_data_product"] = "Web Scraper API (Crawl)"
        return result

    markdown = await _call_with_circuit_breaker(
        "unlocker", unlocker_scrape, url, threshold=2, cooldown=15.0
    )
    if markdown:
        return {
            "body": markdown,
            "partial": True,
            "tier": 2,
            "source": "brightdata_unlocker",
            "bright_data_product": "Web Unlocker",
        }

    body = await _call_with_circuit_breaker(
        "browser", browser_render, url, threshold=2, cooldown=15.0
    )
    if body:
        return {
            "body": body,
            "partial": True,
            "tier": 3,
            "source": "brightdata_browser",
            "bright_data_product": "Scraping Browser (MCP Act)",
        }

    logger.warning(f"All extraction tiers exhausted for {url}")
    return {"body": None, "partial": True, "tier": 0, "source": "none"}


async def search_with_fallback(query: str, max_results: int = 8) -> list[dict]:
    """Multi-tier SERP strategy: MCP Discover → Bright Data SERP → DuckDuckGo, with Redis cache."""
    cached = await get_cached_serp(query)
    if cached is not None:
        logger.info(f"SERP cache hit: {query[:60]}")
        return cached

    mcp_results = await _call_with_circuit_breaker(
        "mcp_discover", mcp_discover, query, threshold=3, cooldown=30.0
    )
    if mcp_results:
        logger.info(f"MCP Discover returned {len(mcp_results)} results")
        for r in mcp_results:
            r["bright_data_product"] = "MCP Server — Discover"
        await set_cached_serp(query, mcp_results)
        return mcp_results

    results = await _call_with_circuit_breaker(
        "serp_api", serp_search, query, max_results, threshold=2, cooldown=15.0
    )
    if results:
        await set_cached_serp(query, results)
        return results

    logger.info("BrightData SERP exhausted, falling back to DuckDuckGo")
    try:
        fallback = await asyncio.to_thread(_duckduckgo_search, query, max_results)
        if fallback:
            await set_cached_serp(query, fallback)
            return fallback
    except Exception as e:
        logger.warning(f"DuckDuckGo fallback failed: {e}")

    return []


_SEMAPHORE = asyncio.Semaphore(4)


async def _fetch_one(url: str) -> dict:
    async with _SEMAPHORE:
        return await extract_article_content(url)


async def fetch_all_sources(urls: list[str]) -> list[dict]:
    tasks = [_fetch_one(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if isinstance(r, dict) and r]


async def health_check() -> dict:
    """Check status of all circuit breakers from Redis."""
    client = await _get_redis()
    if client is None:
        return {"circuit_breakers": "Redis not available"}

    result = {}
    cursor = 0
    while True:
        cursor, keys = await client.scan(cursor=cursor, match="cb:*", count=100)
        for key in keys:
            name = key.split(":", 1)[1]
            failures = int(await client.hget(key, "failures") or 0)
            last_fail = float(await client.hget(key, "last") or 0)
            threshold = 3
            is_open = failures >= threshold
            result[name] = {
                "is_open": is_open,
                "failures": failures,
                "cooldown_remaining": (max(0, 30.0 - (time.time() - last_fail)) if is_open else 0),
            }
        if cursor == 0:
            break

    return {"circuit_breakers": result}
