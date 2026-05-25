import yfinance as yf
from app.services.supabase_db import (
    save_financial_result,
    get_saved_financial_result,
)
from datetime import (
    datetime,
)

from app.logging_config import (
    get_logger,
)

from app.services.cache import (
    get_job_query,
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

from app.utils.search import (
    search_claim,
)

logger = get_logger(
    "financial"
)


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
                    points.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "price": round(float(price), 2),
                    })
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
    logger.info(
        f"Financial analysis started: {query}"
    )

    try:
        await set_progress(
            job_id,
            "Searching for financial data...",
        )

        search_results = await search_claim(query, max_results=8)

        search_context = ""
        if search_results:
            lines = []
            for i, r in enumerate(search_results, 1):
                lines.append(f'{i}. "{r["title"]}"')
                lines.append(f'   URL: {r["url"]}')
                lines.append(f'   Snippet: {r["snippet"]}')
            search_context = "\n".join(lines)

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
        if search_results:
            for r in search_results[:5]:
                sources.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "credibility": "Medium",
                    "stance": ai_analysis.get("price_trend", "Neutral"),
                    "summary": r.get("snippet", "")[:200],
                    "date": datetime.now().strftime("%Y-%m-%d"),
                })
        else:
            sources.append({
                "title": "Web Search",
                "url": "https://duckduckgo.com",
                "credibility": "Medium",
                "stance": ai_analysis.get("price_trend", "Neutral"),
                "summary": "Analysis based on available data.",
                "date": datetime.now().strftime("%Y-%m-%d"),
            })

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

        await push_claim_to_history({
            "jobId": job_id,
            "claim": f"[FINANCIAL] {query}",
            "status": STATUS_DONE,
            "createdAt": datetime.now().isoformat(),
        })

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
    saved = (
        await get_saved_financial_result(
            job_id
        )
    )

    if saved:
        logger.info(
            f"Financial result found: {job_id}"
        )

        return saved.get(
            "result"
        )

    return {
        "status": "processing",
        "jobId": job_id,
        "progress": "Searching for financial data...",
    }