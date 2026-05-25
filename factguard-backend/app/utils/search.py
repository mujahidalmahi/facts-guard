import asyncio
import os

from ddgs import DDGS

from app.logging_config import (
    get_logger,
)

logger = get_logger(
    "search"
)

SEARCH_RESULTS_MAX = 5


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
    """
    BrightData-ready provider.

    Currently falls back to DDGS.

    Replace later with:
    BrightData SERP API
    BrightData Browser API
    BrightData Scraper API
    """

    logger.info(
        "BrightData provider not configured, "
        "falling back to DDGS"
    )

    return _duckduckgo_search(
        query,
        max_results,
    )


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