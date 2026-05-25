import asyncio
import os

import httpx
from ddgs import DDGS

from app.logging_config import (
    get_logger,
)

logger = get_logger(
    "search"
)

SEARCH_RESULTS_MAX = 8

BRIGHTDATA_ENDPOINT = (
    "https://api.brightdata.com/request"
)

BRIGHTDATA_UNLOCKER = (
    "https://api.brightdata.com/request"
)


def _duckduckgo_search(
    query: str,
    max_results: int,
) -> list[dict]:
    try:
        results = list(
            DDGS().text(
                query,
                max_results=max_results,
            )
        )

        return [
            {
                "title":
                    r.get(
                        "title",
                        "",
                    ),

                "url":
                    r.get(
                        "href",
                        "",
                    ),

                "snippet":
                    r.get(
                        "body",
                        "",
                    ),

                "source":
                    "duckduckgo",
            }
            for r in results
        ]

    except Exception as e:
        logger.warning(
            f"DuckDuckGo search failed: {e}"
        )

        return []


def _brightdata_search(
    query: str,
    max_results: int,
) -> list[dict]:
    api_key = os.getenv(
        "BRIGHTDATA_API_KEY",
        "",
    )

    if not api_key:
        logger.warning(
            "BRIGHTDATA_API_KEY missing — "
            "falling back to DDGS"
        )

        return _duckduckgo_search(
            query,
            max_results,
        )

    try:
        payload = {
            "zone": "serp",
            "url":
                "https://www.google.com/"
                f"search?q={query}"
                f"&num={max_results}",
            "format": "json",
            "country": "us",
        }

        headers = {
            "Authorization":
                f"Bearer {api_key}",
            "Content-Type":
                "application/json",
        }

        resp = httpx.post(
            BRIGHTDATA_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=20,
        )

        resp.raise_for_status()
        data = resp.json()
        organic = data.get(
            "organic",
            [],
        )
        results = []

        for r in organic[:max_results]:
            results.append(
                {
                    "title":
                        r.get(
                            "title",
                            "",
                        ),
                    "url":
                        r.get(
                            "link",
                            r.get(
                                "url",
                                "",
                            ),
                        ),
                    "snippet":
                        r.get(
                            "snippet",
                            r.get(
                                "description",
                                "",
                            ),
                        ),
                    "source":
                        "brightdata",
                }
            )

        logger.info(
            f"BrightData SERP returned "
            f"{len(results)} results"
        )

        return results

    except Exception as e:
        logger.warning(
            f"BrightData SERP failed: {e} "
            "— falling back to DDGS"
        )

        return _duckduckgo_search(
            query,
            max_results,
        )


def brightdata_scrape_product(
    product_url: str,
) -> str:
    api_key = os.getenv(
        "BRIGHTDATA_API_KEY",
        "",
    )

    if not api_key:
        return ""

    try:
        payload = {
            "zone": "unlocker",
            "url": product_url,
            "format": "raw",
        }

        resp = httpx.post(
            BRIGHTDATA_UNLOCKER,
            json=payload,
            headers={
                "Authorization":
                    f"Bearer {api_key}"
            },
            timeout=30,
        )

        return resp.text[:4000]

    except Exception as e:
        logger.warning(
            f"Web Unlocker scrape failed: {e}"
        )

        return ""


def _search_sync(
    query: str,
    max_results: int,
) -> list[dict]:
    provider = os.getenv(
        "SEARCH_PROVIDER",
        "brightdata",
    )

    if (
        provider
        == "brightdata"
    ):
        return _brightdata_search(
            query,
            max_results,
        )

    return _duckduckgo_search(
        query,
        max_results,
    )


async def search_claim(
    claim: str,
    max_results: int = SEARCH_RESULTS_MAX,
) -> list[dict]:
    try:
        results = (
            await asyncio.to_thread(
                _search_sync,
                claim,
                max_results,
            )
        )

        if results:
            logger.info(
                f"Web search returned "
                f"{len(results)} results"
            )
        else:
            logger.info(
                "Web search returned no results"
            )

        return results

    except Exception as e:
        logger.warning(
            f"Web search failed: {str(e)}"
        )

        return []
