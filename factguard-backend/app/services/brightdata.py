import re
from urllib.parse import quote

import httpx
from typing import Optional
from app.config import settings
from app.logging_config import get_logger
from app.services.browser_cache import (
    get_cached_browser_extract,
    set_cached_browser_extract,
)

logger = get_logger("brightdata")

BRIGHTDATA_ENDPOINT = "https://api.brightdata.com/request"
BRIGHTDATA_CRAWL_ENDPOINT = "https://api.brightdata.com/crawl"
BRIGHTDATA_BROWSER_ENDPOINT = "https://api.brightdata.com/browser"
BRIGHTDATA_MCP_ENDPOINT = "https://api.brightdata.com/mcp"

PAYWALL_DOMAINS = [
    "bloomberg.com",
    "wsj.com",
    "ft.com",
    "barrons.com",
    "nytimes.com",
    "washingtonpost.com",
    "forbes.com",
    "economist.com",
    "latimes.com",
    "foreignpolicy.com",
]

SNIPPET_SUBSTRING_INDICATORS = [
    "sign in",
    "subscribe",
    "unlock",
    "paywall",
    "limited",
    "premium",
]

_serp_zone: str | None = None
_serp_zone_discovered: bool = False


def _get_api_key() -> str:
    return settings.BRIGHTDATA_API_KEY or ""


def _headers() -> dict:
    key = _get_api_key()
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


async def _discover_serp_zone() -> str | None:
    """Discover the user's BrightData SERP zone name via the API."""
    key = _get_api_key()
    if not key:
        return None

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.brightdata.com/zone/get_active_zones",
                headers=_headers(),
                timeout=10,
            )
            if resp.is_success:
                zones = resp.json()
                for zone in zones:
                    if zone.get("type") == "serp":
                        name = zone["name"]
                        logger.info(f"Discovered SERP zone: {name}")
                        return name
                logger.info("No SERP zone found in BrightData account")
                return None
            logger.warning(f"Failed to list zones: {resp.status_code} {resp.text[:300]}")
            return None
    except Exception as e:
        logger.warning(f"Zone discovery failed: {e}")
        return None


async def serp_search(query: str, max_results: int = 8, engine: str = "google") -> list[dict]:
    api_key = _get_api_key()
    if not api_key:
        logger.warning("BRIGHTDATA_API_KEY missing")
        return []

    global _serp_zone, _serp_zone_discovered
    if not _serp_zone_discovered:
        _serp_zone_discovered = True
        if settings.BRIGHTDATA_SERP_ZONE:
            _serp_zone = settings.BRIGHTDATA_SERP_ZONE
            logger.info(f"Using configured SERP zone: {_serp_zone}")
        else:
            _serp_zone = await _discover_serp_zone()

    if _serp_zone is None:
        logger.warning("SERP zone not configured")
        return []

    try:
        encoded_query = quote(query)
        if engine == "bing":
            search_url = f"https://www.bing.com/search?q={encoded_query}&count={max_results}"
            source_label = "brightdata_bing"
        else:
            search_url = f"https://www.google.com/search?q={encoded_query}&num={max_results}&hl=en&gl=us&brd_json=1"
            source_label = "brightdata_serp"

        payload = {
            "zone": _serp_zone,
            "url": search_url,
            "format": "raw",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(BRIGHTDATA_ENDPOINT, json=payload, headers=_headers(), timeout=20)
            if not resp.is_success:
                logger.warning(f"BrightData SERP ({engine}) error {resp.status_code}: {resp.text[:500]}")
            resp.raise_for_status()
            data = resp.json()

        organic = data.get("organic", [])
        results = []
        for r in organic[:max_results]:
            results.append({
                "title": r.get("title", ""),
                "url": r.get("link", r.get("url", "")),
                "snippet": r.get("snippet", r.get("description", "")),
                "source": source_label,
            })
        logger.info(f"BrightData SERP ({engine}) returned {len(results)} results")
        return results
    except Exception as e:
        logger.warning(f"BrightData SERP ({engine}) failed: {e}")
        return []


async def crawl_extract(url: str) -> Optional[dict]:
    """Tier 1: BrightData Crawl API for structured article extraction."""
    api_key = _get_api_key()
    if not api_key:
        return None
    try:
        payload = {
            "zone": "crawl",
            "url": url,
            "format": "json",
            "extract": {
                "title": True,
                "author": True,
                "date": True,
                "body": True,
                "metadata": True,
            },
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(BRIGHTDATA_ENDPOINT, json=payload, headers=_headers(), timeout=30)
            resp.raise_for_status()
            data = resp.json()
        result = {
            "title": data.get("title", ""),
            "author": data.get("author"),
            "date": data.get("date"),
            "body": data.get("body", "")[:5000],
            "metadata": data.get("metadata", {}),
            "source": "brightdata_crawl",
        }
        logger.info(f"Crawl API extracted: {url}")
        return result
    except Exception as e:
        logger.warning(f"Crawl API failed for {url}: {e}")
        return None


async def unlocker_scrape(url: str) -> Optional[str]:
    """Tier 2: Web Unlocker for paywall bypass."""
    api_key = _get_api_key()
    if not api_key:
        return None
    try:
        payload = {
            "zone": "unlocker",
            "url": url,
            "format": "raw",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(BRIGHTDATA_ENDPOINT, json=payload, headers=_headers(), timeout=30)
            resp.raise_for_status()
            text = resp.text[:5000]
        logger.info(f"Web Unlocker scraped: {url}")
        return text
    except Exception as e:
        logger.warning(f"Web Unlocker failed for {url}: {e}")
        return None


async def browser_render(url: str) -> Optional[str]:
    """Scraping Browser via BrightData CDP WebSocket proxy."""
    wss_url = settings.BRIGHTDATA_WSS
    if not wss_url:
        logger.warning("BRIGHTDATA_WSS not configured — skipping browser render")
        return None
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            logger.info(f"Connecting to BrightData CDP...")
            browser = await p.chromium.connect_over_cdp(wss_url, timeout=settings.BROWSER_TIMEOUT * 1000 + 5000)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=settings.BROWSER_TIMEOUT * 1000)
            body_text = await page.evaluate("() => document.body.innerText")
            await page.close()
            await browser.close()

        text = (body_text or "")[:5000]
        logger.info(f"Scraping Browser rendered: {url} ({len(text)} chars)")
        return text
    except Exception as e:
        logger.warning(f"Scraping Browser (CDP) failed for {url}: {e}")
        return None


def should_use_browser(
    url: str,
    snippet: str,
) -> bool:
    if not snippet or len(snippet.strip()) < 100:
        return True

    snippet_lower = snippet.lower()
    for indicator in SNIPPET_SUBSTRING_INDICATORS:
        if indicator in snippet_lower:
            return True

    domain_match = re.search(
        r"https?://([^/]+)",
        url,
    )
    if domain_match:
        domain = domain_match.group(1).lower()
        for paywall_domain in PAYWALL_DOMAINS:
            if paywall_domain in domain:
                return True

    return False


async def browser_extract_text(
    url: str,
) -> str | None:
    cached = await get_cached_browser_extract(url)
    if cached is not None:
        logger.info(f"Browser cache hit: {url}")
        return cached

    text = await browser_render(url)
    if text:
        await set_cached_browser_extract(url, text)

    return text


async def mcp_discover(query: str) -> list[dict]:
    """BrightData MCP Discover action."""
    api_key = _get_api_key()
    if not api_key:
        return []
    try:
        payload = {
            "action": "discover",
            "query": query,
            "max_results": 8,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(BRIGHTDATA_MCP_ENDPOINT, json=payload, headers=_headers(), timeout=20)
            resp.raise_for_status()
            data = resp.json()
        results = data.get("results", [])
        logger.info(f"MCP Discover returned {len(results)} results")
        return results
    except Exception as e:
        logger.warning(f"MCP Discover failed: {e}")
        return []


async def proxy_request(url: str, country: str = "us") -> Optional[str]:
    """Request via BrightData proxy network with geo-targeting."""
    api_key = _get_api_key()
    if not api_key:
        return None
    try:
        payload = {
            "zone": "proxy",
            "url": url,
            "format": "raw",
            "country": country,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(BRIGHTDATA_ENDPOINT, json=payload, headers=_headers(), timeout=30)
            resp.raise_for_status()
            text = resp.text[:5000]
        logger.info(f"Proxy request completed: {url} ({country})")
        return text
    except Exception as e:
        logger.warning(f"Proxy request failed for {url}: {e}")
        return None
