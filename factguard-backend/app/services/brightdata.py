from urllib.parse import quote

import httpx
from typing import Optional
from app.config import settings
from app.logging_config import get_logger

logger = get_logger("brightdata")

BRIGHTDATA_ENDPOINT = "https://api.brightdata.com/request"
BRIGHTDATA_CRAWL_ENDPOINT = "https://api.brightdata.com/crawl"
BRIGHTDATA_BROWSER_ENDPOINT = "https://api.brightdata.com/browser"
BRIGHTDATA_MCP_ENDPOINT = "https://api.brightdata.com/mcp"

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


async def serp_search(query: str, max_results: int = 8) -> list[dict]:
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
        payload = {
            "zone": _serp_zone,
            "url": f"https://www.google.com/search?q={encoded_query}&num={max_results}&hl=en&gl=us&brd_json=1",
            "format": "raw",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(BRIGHTDATA_ENDPOINT, json=payload, headers=_headers(), timeout=20)
            if not resp.is_success:
                logger.warning(f"BrightData SERP error {resp.status_code}: {resp.text[:500]}")
            resp.raise_for_status()
            data = resp.json()

        organic = data.get("organic", [])
        results = []
        for r in organic[:max_results]:
            results.append({
                "title": r.get("title", ""),
                "url": r.get("link", r.get("url", "")),
                "snippet": r.get("snippet", r.get("description", "")),
                "source": "brightdata_serp",
            })
        logger.info(f"BrightData SERP returned {len(results)} results")
        return results
    except Exception as e:
        logger.warning(f"BrightData SERP failed: {e}")
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
    """Tier 3: Scraping Browser for JS-heavy pages."""
    api_key = _get_api_key()
    if not api_key:
        return None
    try:
        payload = {
            "zone": "scraping_browser",
            "url": url,
            "action": "navigate",
            "wait_for": "networkidle",
            "timeout": 15000,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(BRIGHTDATA_BROWSER_ENDPOINT, json=payload, headers=_headers(), timeout=30)
            resp.raise_for_status()
            data = resp.json()
        body = data.get("body", "")[:5000]
        logger.info(f"Scraping Browser rendered: {url}")
        return body
    except Exception as e:
        logger.warning(f"Scraping Browser failed for {url}: {e}")
        return None


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
