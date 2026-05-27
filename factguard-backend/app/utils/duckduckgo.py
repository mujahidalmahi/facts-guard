from ddgs import DDGS

from app.logging_config import get_logger

logger = get_logger("duckduckgo")


def search(query: str, max_results: int = 8) -> list[dict]:
    """DuckDuckGo text search fallback. Synchronous."""
    try:
        results = list(
            DDGS().text(
                query,
                max_results=max_results,
            )
        )

        return [
            {
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
                "source": "duckduckgo",
            }
            for r in results
        ]

    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}")
        return []
