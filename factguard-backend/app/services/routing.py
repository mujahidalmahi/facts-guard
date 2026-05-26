import asyncio
import time
from typing import Any, Callable
from dataclasses import dataclass

from app.logging_config import get_logger
from app.services.brightdata import (
    crawl_extract,
    unlocker_scrape,
    browser_render,
    serp_search,
    mcp_discover,
)
from app.utils.duckduckgo import search as _duckduckgo_search

logger = get_logger("routing")


@dataclass
class CircuitBreakerState:
    failures: int = 0
    last_failure_time: float = 0
    is_open: bool = False
    threshold: int = 3
    cooldown: float = 30.0


_circuit_breakers: dict[str, CircuitBreakerState] = {}


def _get_cb(name: str, threshold: int = 3, cooldown: float = 30.0) -> CircuitBreakerState:
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreakerState(threshold=threshold, cooldown=cooldown)
    return _circuit_breakers[name]


async def _call_with_circuit_breaker(
    name: str,
    func: Callable,
    *args,
    threshold: int = 3,
    cooldown: float = 30.0,
) -> Any:
    cb = _get_cb(name, threshold, cooldown)

    if cb.is_open:
        if time.time() - cb.last_failure_time > cb.cooldown:
            cb.is_open = False
            cb.failures = 0
            logger.info(f"Circuit breaker '{name}' reset (cooldown expired)")
        else:
            logger.warning(f"Circuit breaker '{name}' is OPEN — skipping")
            return None

    try:
        result = await func(*args)
        if result is not None and result != []:
            cb.failures = 0
            return result
        raise ValueError(f"Empty result from {name}")
    except Exception as e:
        cb.failures += 1
        cb.last_failure_time = time.time()
        logger.warning(f"Circuit breaker '{name}' failure {cb.failures}/{cb.threshold}: {e}")
        if cb.failures >= cb.threshold:
            cb.is_open = True
            logger.warning(f"Circuit breaker '{name}' OPENED after {cb.failures} failures")
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
    """Multi-tier SERP strategy: MCP Discover → Bright Data SERP → DuckDuckGo."""
    mcp_results = await _call_with_circuit_breaker(
        "mcp_discover", mcp_discover, query, threshold=2, cooldown=15.0
    )
    if mcp_results:
        logger.info(f"MCP Discover returned {len(mcp_results)} results")
        for r in mcp_results:
            r["bright_data_product"] = "MCP Server — Discover"
        return mcp_results

    results = await _call_with_circuit_breaker(
        "serp_api", serp_search, query, max_results, threshold=2, cooldown=15.0
    )
    if results:
        return results

    logger.info("BrightData SERP exhausted, falling back to DuckDuckGo")
    try:
        fallback = await asyncio.to_thread(_duckduckgo_search, query, max_results)
        if fallback:
            return fallback
    except Exception as e:
        logger.warning(f"DuckDuckGo fallback failed: {e}")

    return []


async def health_check() -> dict:
    """Check status of all circuit breakers."""
    return {
        name: {
            "is_open": cb.is_open,
            "failures": cb.failures,
            "cooldown_remaining": max(0, cb.cooldown - (time.time() - cb.last_failure_time)) if cb.is_open else 0,
        }
        for name, cb in _circuit_breakers.items()
    }
