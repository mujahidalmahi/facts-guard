import yfinance as yf
from asyncio import Semaphore
from app.services.supabase_db import (
    save_financial_result,
    update_financial_result,
    get_saved_financial_result,
)
from datetime import (
    datetime,
    timezone,
)

from app.logging_config import (
    get_logger,
)

from app.services.cache import (
    set_job_query,
    set_progress,
    push_claim_to_history,
    get_cached_serp,
    set_cached_serp,
)

from app.services.deepseek import (
    deepseek_financial_analysis,
)

from app.utils.constants import (
    STATUS_DONE,
    STATUS_ERROR,
)

import asyncio

from app.services.brightdata import (
    serp_search,
    browser_extract_text,
)

from app.utils.duckduckgo import search as ddg_search

logger = get_logger("financial")

_browser_sem = Semaphore(2)


async def create_financial_query(
    query: str,
    job_id: str,
) -> str:
    await set_job_query(job_id, query)
    return job_id


YFINANCE_SYMBOLS = {
    "BITCOIN": "BTC-USD",
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "ETHEREUM": "ETH-USD",
    "TESLA": "TSLA",
    "APPLE": "AAPL",
    "NVIDIA": "NVDA",
    "S&P": "^GSPC",
    "SPX": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW": "^DJI",
    "GOLD": "GC=F",
    "SILVER": "SI=F",
    "SILICON": "^SOX",
    "SEMICONDUCTOR": "^SOX",
    "SMH": "SMH",
    "CRUDE": "CL=F",
    "OIL": "CL=F",
}


def _try_yfinance_chart(query: str) -> dict | None:
    q = query.strip().upper()
    for keyword, symbol in YFINANCE_SYMBOLS.items():
        if keyword in q:
            try:
                ticker = yf.Ticker(symbol)
                history = ticker.history(period="1mo")
                if history.empty:
                    return None
                points = []
                for date, row in history.iterrows():
                    price = row.get("Close")
                    if price is None:
                        continue
                    points.append(
                        {
                            "date": date.strftime("%Y-%m-%d"),
                            "price": round(float(price), 2),
                        }
                    )
                if not points:
                    return None
                prices = [p["price"] for p in points]
                return {
                    "label": symbol,
                    "unit": "USD",
                    "current_price": prices[-1],
                    "change_24h": "Live",
                    "change_7d": "Live",
                    "all_time_high": max(prices),
                    "data": points,
                }
            except Exception:
                return None
    return None


async def _run_serp_search(query: str) -> list[dict]:
    """Run SERP search across Google, Bing, and DuckDuckGo with Redis caching."""
    cached = await get_cached_serp(query)
    if cached is not None:
        logger.info(f"SERP cache hit for: {query[:60]}")
        return cached

    google_task = serp_search(query, max_results=5)
    bing_task = serp_search(query, max_results=5, engine="bing")
    ddg_task = asyncio.to_thread(ddg_search, query, 5)

    google_results, bing_results, ddg_results = await asyncio.gather(
        google_task, bing_task, ddg_task, return_exceptions=True
    )

    all_results = []
    seen_urls = set()
    for results in [google_results, bing_results, ddg_results]:
        if isinstance(results, list) and results:
            for r in results:
                url = r.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(r)

    logger.info(
        f"Found {len(all_results)} unique results "
        f"(Google: {len(google_results) if isinstance(google_results, list) else 0}, "
        f"Bing: {len(bing_results) if isinstance(bing_results, list) else 0}, "
        f"DDG: {len(ddg_results) if isinstance(ddg_results, list) else 0})"
    )

    if all_results:
        await set_cached_serp(query, all_results)

    return all_results


async def process_financial_analysis(
    query_id: str,
    query: str,
    job_id: str,
):
    logger.info(f"Financial analysis started: {query}")

    try:
        await set_progress(job_id, "Searching Google, Bing & DuckDuckGo...")

        # Start both SERP and WSS tasks in parallel
        serp_task = asyncio.create_task(_run_serp_search(query))
        wss_task = asyncio.create_task(_enrich_with_wss(job_id, query, serp_task))

        # Phase 1: await SERP results — fast (~5s)
        all_results = await serp_task
        graph_data = _try_yfinance_chart(query)

        sources = []
        if all_results:
            for r in all_results[:5]:
                url = r.get("url", "")
                sources.append({
                    "title": r.get("title", ""),
                    "url": url,
                    "credibility": "Medium",
                    "stance": "Neutral",
                    "summary": (r.get("snippet", "") or "")[:200],
                    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                })
        else:
            sources.append({
                "title": "Web Search",
                "url": "https://duckduckgo.com",
                "credibility": "Medium",
                "stance": "Neutral",
                "summary": "No results found.",
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            })

        result = {
            "mode": "financial",
            "status": STATUS_DONE,
            "jobId": job_id,
            "query": query,
            "graph_data": graph_data,
            "sources": sources,
            "enriching": True,
        }
        await save_financial_result(job_id, query, result)

        await push_claim_to_history({
            "jobId": job_id,
            "claim": f"[FINANCIAL] {query}",
            "status": STATUS_DONE,
            "createdAt": datetime.now(timezone.utc).isoformat(),
        })

        logger.info(f"Phase 1 complete (initial result saved): {job_id}")

        # Phase 2: await WSS enrichment — slow (~50s)
        await wss_task

    except Exception as e:
        logger.error(f"Financial analysis failed: {e}")

        error_result = {
            "mode": "financial",
            "status": STATUS_ERROR,
            "jobId": job_id,
            "query": query,
            "analysis": {
                "signal": "HOLD",
                "signal_strength": "Moderate",
                "price_trend": "Sideways",
                "summary": f"Analysis failed: {str(e)}",
                "risk_level": "Medium",
                "prediction_30d": "Unavailable",
                "confidence": "Low",
                "key_factors": [],
            },
        }
        await save_financial_result(job_id, query, error_result)


async def _enrich_with_wss(
    job_id: str,
    query: str,
    serp_task: asyncio.Task,
):
    """Phase 2: awaits SERP results, extracts articles via WSS, runs AI, updates result."""
    try:
        # Wait for SERP to provide URLs
        all_results = await serp_task

        await set_progress(job_id, "Extracting articles via browser...")

        top_urls = [r["url"] for r in all_results[:5] if r.get("url")]
        browser_texts: dict[str, str] = {}
        if top_urls:
            async def _extract_one(url: str) -> tuple[str, str | None]:
                async with _browser_sem:
                    text = await browser_extract_text(url)
                    return url, text
            extracted_list = await asyncio.gather(
                *[_extract_one(url) for url in top_urls],
                return_exceptions=True,
            )
            for item in extracted_list:
                if isinstance(item, tuple):
                    url, extracted = item
                    if isinstance(extracted, str) and extracted:
                        browser_texts[url] = extracted

        search_context_lines = []
        if all_results:
            for i, r in enumerate(all_results[:8], 1):
                search_context_lines.append(f'{i}. "{r["title"]}"')
                search_context_lines.append(f'   URL: {r["url"]}')
                search_context_lines.append(f'   Source: {r.get("source", "web")}')
                search_context_lines.append(f'   Snippet: {r.get("snippet", "")}')
            search_context = "\n".join(search_context_lines)
            for url in top_urls:
                if url in browser_texts:
                    search_context += f"\n\nFULL ARTICLE TEXT (from {url}):\n{browser_texts[url][:3000]}"

        enriched_analysis = await deepseek_financial_analysis(query, search_context)

        sources = []
        for r in all_results[:5]:
            url = r.get("url", "")
            source = {
                "title": r.get("title", ""),
                "url": url,
                "credibility": "Medium",
                "stance": enriched_analysis.get("price_trend", "Neutral"),
                "summary": (r.get("snippet", "") or "")[:200],
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            }
            if url in browser_texts:
                source["extraction"] = "browser"
            sources.append(source)

        enriched_result = {
            "mode": "financial",
            "status": STATUS_DONE,
            "jobId": job_id,
            "query": query,
            "graph_data": _try_yfinance_chart(query),
            "analysis": enriched_analysis,
            "sources": sources,
            "enriching": False,
        }

        await update_financial_result(job_id, enriched_result)
        logger.info(f"Enrichment complete: {job_id}")

    except Exception as e:
        logger.error(f"WSS enrichment failed: {e}")
        try:
            saved = await get_saved_financial_result(job_id)
            if saved:
                r = saved.get("result")
                if isinstance(r, str):
                    import json
                    r = json.loads(r)
                if isinstance(r, dict):
                    r["enriching"] = False
                    await update_financial_result(job_id, r)
        except Exception as e2:
            logger.error(f"Failed to clear enriching flag: {e2}")


async def get_full_financial_result(
    job_id: str,
):
    saved = await get_saved_financial_result(job_id)

    if saved:
        logger.info(f"Financial result found: {job_id}")

        return saved.get("result")

    return {
        "status": "processing",
        "jobId": job_id,
        "progress": "Searching for financial data...",
    }
