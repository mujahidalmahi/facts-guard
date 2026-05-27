import yfinance as yf
from app.services.supabase_db import (
    save_financial_result,
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


async def process_financial_analysis(
    query_id: str,
    query: str,
    job_id: str,
):
    logger.info(f"Financial analysis started: {query}")

    try:
        await set_progress(
            job_id,
            "Searching Google, Bing & DuckDuckGo...",
        )

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

        search_context = ""
        if all_results:
            lines = []
            for i, r in enumerate(all_results[:8], 1):
                lines.append(f'{i}. "{r["title"]}"')
                lines.append(f'   URL: {r["url"]}')
                lines.append(f'   Source: {r.get("source", "web")}')
                lines.append(f'   Snippet: {r.get("snippet", "")}')
            search_context = "\n".join(lines)

        browser_texts: dict[str, str] = {}
        if all_results:
            await set_progress(
                job_id,
                "Extracting articles via browser...",
            )
            top_urls = [r["url"] for r in all_results[:5] if r.get("url")]
            if top_urls:
                extracted_list = await asyncio.gather(
                    *[browser_extract_text(url) for url in top_urls],
                    return_exceptions=True,
                )
                for url, extracted in zip(top_urls, extracted_list):
                    if isinstance(extracted, str) and extracted:
                        browser_texts[url] = extracted
                        search_context += (
                            "\n\nFULL ARTICLE TEXT " f"(from {url}):\n" f"{extracted[:3000]}"
                        )

        await set_progress(
            job_id,
            "Running AI analysis...",
        )

        ai_analysis = await deepseek_financial_analysis(
            query,
            search_context,
        )

        graph_data = _try_yfinance_chart(query)

        sources = []
        if all_results:
            for r in all_results[:5]:
                url = r.get("url", "")
                source = {
                    "title": r.get("title", ""),
                    "url": url,
                    "credibility": "Medium",
                    "stance": ai_analysis.get("price_trend", "Neutral"),
                    "summary": (r.get("snippet", "") or "")[:200],
                    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                }
                if url in browser_texts:
                    source["extraction"] = "browser"
                sources.append(source)
        else:
            sources.append(
                {
                    "title": "Web Search",
                    "url": "https://duckduckgo.com",
                    "credibility": "Medium",
                    "stance": ai_analysis.get("price_trend", "Neutral"),
                    "summary": "Analysis based on available data.",
                    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                }
            )

        result = {
            "mode": "financial",
            "status": STATUS_DONE,
            "jobId": job_id,
            "query": query,
            "graph_data": graph_data,
            "analysis": ai_analysis,
            "sources": sources,
        }

        await save_financial_result(job_id, query, result)

        await push_claim_to_history(
            {
                "jobId": job_id,
                "claim": f"[FINANCIAL] {query}",
                "status": STATUS_DONE,
                "createdAt": datetime.now(timezone.utc).isoformat(),
            }
        )

        logger.info(f"Financial analysis completed: {job_id}")

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
