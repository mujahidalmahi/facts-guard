import asyncio

from ddgs import DDGS

from app.logging_config import get_logger

logger = get_logger("search")

SEARCH_RESULTS_MAX = 5


def _search_sync(query: str, max_results: int) -> list[dict]:
    try:
        results = list(DDGS().text(query, max_results=max_results))
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
            }
            for r in results
        ]
    except Exception:
        return []


async def search_claim(claim: str, max_results: int = SEARCH_RESULTS_MAX) -> list[dict]:
    try:
        results = await asyncio.to_thread(_search_sync, claim, max_results)
        if results:
            logger.info(f"Web search returned {len(results)} results for claim")
        else:
            logger.info("Web search returned no results")
        return results
    except Exception as e:
        logger.warning(f"Web search failed: {str(e)}")
        return []
