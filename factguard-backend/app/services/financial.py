import json

import yfinance as yf
from asyncio import Semaphore
from app.utils.parsing import parse_json_response
from app.services.supabase_db import (
    save_financial_result,
    update_financial_result,
    get_saved_financial_result,
)
from datetime import (
    datetime,
    timezone,
)

from app.config import settings
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

FINANCIAL_SYSTEM_PROMPT = """You are ORACLE, FactGuard's quant-grade market
intelligence engine. You synthesize real-time web data, price signals, and
macroeconomic context into institutional-quality market briefs.

You serve: retail investors needing clarity, journalists covering markets,
and analysts who need a rapid second opinion.

## DATA INPUTS YOU RECEIVE
1. Live web search results (BrightData SERP) — news, analyst reports, filings
2. yFinance OHLCV data (when available) — exact price, volume, 30-day history
3. The user's specific query

## ANALYSIS FRAMEWORK
Inside <scratchpad>:
 A. PRICE CONTEXT: Current price vs 7d, 30d, 52w. Volume trend. Volatility.
 B. CATALYST SCAN: Identify all bullish and bearish catalysts from evidence.
 C. SENTIMENT READ: Is news sentiment broadly positive, negative, or mixed?
 D. RISK MATRIX: List the top 3 specific risks (not generic "market risk").
 E. SCENARIO PLANNING: Build three 30-day scenarios with probability weights.

## SIGNAL CLASSIFICATION
Bullish — Price + momentum + catalyst alignment. Risk-reward favors longs.
Bearish — Deteriorating fundamentals, negative catalysts, weak technicals.
Neutral — Mixed signals, consolidation, or insufficient data.

## OUTPUT CONTRACT — VALID JSON ONLY
{
  "signal": "Bullish|Bearish|Neutral",
  "signal_strength": <int 0-100>,
  "asset": "Asset name and ticker",
  "current_price": "price string with currency",
  "price_trend": "Up|Down|Sideways",
  "trend_magnitude": "Strong|Moderate|Weak",
  "risk_level": "High|Medium|Low",
  "risk_catalysts": ["specific risk 1", "specific risk 2", "specific risk 3"],
  "key_factors": ["factor1", "factor2", "factor3"],
  "summary": "3-4 sentence institutional-quality brief. Cite specific numbers.",
  "prediction_30d": {
    "bull_case": "Target + probability + catalyst required",
    "base_case": "Target + probability + assumption",
    "bear_case": "Target + probability + trigger"
  },
  "sources": [{"title": "...", "url": "...", "date": "YYYY-MM-DD"}],
  "data_freshness": "real-time|intraday|daily|stale"
}"""

FINANCIAL_USER_PROMPT = """Today's date: {today}
Query: {query}

## WEB SEARCH RESULTS
Use these results as your PRIMARY evidence. Weight by source tier (see system prompt).
If fewer than 3 Tier-1/2 results are available, set confidence to Low and data_quality to the highest tier available.

{search_context_block}

Reason through the evidence, then return the JSON object."""

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

_browser_sem = Semaphore(5)


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
    "SOLANA": "SOL-USD",
    "SOL": "SOL-USD",
    "DOGE": "DOGE-USD",
    "DOGECOIN": "DOGE-USD",
    "XRP": "XRP-USD",
    "RIPPLE": "XRP-USD",
    "ADA": "ADA-USD",
    "CARDANO": "ADA-USD",
    "DOT": "DOT-USD",
    "POLKADOT": "DOT-USD",
    "AVAX": "AVAX-USD",
    "AVALANCHE": "AVAX-USD",
    "LINK": "LINK-USD",
    "CHAINLINK": "LINK-USD",
    "UNI": "UNI-USD",
    "UNISWAP": "UNI-USD",
    "MATIC": "MATIC-USD",
    "POLYGON": "MATIC-USD",
    "ATOM": "ATOM-USD",
    "COSMOS": "ATOM-USD",
    "LTC": "LTC-USD",
    "LITECOIN": "LTC-USD",
    "BCH": "BCH-USD",
    "BITCOIN CASH": "BCH-USD",
    "TRX": "TRX-USD",
    "TRON": "TRX-USD",
    "NEAR": "NEAR-USD",
    "FTM": "FTM-USD",
    "FANTOM": "FTM-USD",
    "ARB": "ARB-USD",
    "ARBITRUM": "ARB-USD",
    "OP": "OP-USD",
    "OPTIMISM": "OP-USD",
    "APE": "APE-USD",
    "APECOIN": "APE-USD",
    "SAND": "SAND-USD",
    "MANA": "MANA-USD",
    "DECENTRALAND": "MANA-USD",
    "AXS": "AXS-USD",
    "AXIE": "AXS-USD",
    "FIL": "FIL-USD",
    "FILECOIN": "FIL-USD",
    "THETA": "THETA-USD",
    "VET": "VET-USD",
    "VECHAIN": "VET-USD",
    "EOS": "EOS-USD",
    "ALGO": "ALGO-USD",
    "ALGORAND": "ALGO-USD",
    "ICP": "ICP-USD",
    "INTERNET COMPUTER": "ICP-USD",
    "RUNE": "RUNE-USD",
    "THORCHAIN": "RUNE-USD",
    "AAVE": "AAVE-USD",
    "CRV": "CRV-USD",
    "CURVE": "CRV-USD",
    "MKR": "MKR-USD",
    "MAKER": "MKR-USD",
    "COMP": "COMP-USD",
    "COMPOUND": "COMP-USD",
    "SUSHI": "SUSHI-USD",
    "SUSHISWAP": "SUSHI-USD",
    "CAKE": "CAKE-USD",
    "PANCAKESWAP": "CAKE-USD",
    "KSM": "KSM-USD",
    "KUSAMA": "KSM-USD",
    "STX": "STX-USD",
    "STACKS": "STX-USD",
    "IMX": "IMX-USD",
    "IMMUTABLE": "IMX-USD",
    "EGLD": "EGLD-USD",
    "ELROND": "EGLD-USD",
    "HBAR": "HBAR-USD",
    "HEDERA": "HBAR-USD",
    "XLM": "XLM-USD",
    "STELLAR": "XLM-USD",
    "TESLA": "TSLA",
    "APPLE": "AAPL",
    "NVIDIA": "NVDA",
    "META": "META",
    "FACEBOOK": "META",
    "GOOGLE": "GOOGL",
    "GOOGL": "GOOGL",
    "AMAZON": "AMZN",
    "AMZN": "AMZN",
    "MICROSOFT": "MSFT",
    "MSFT": "MSFT",
    "NETFLIX": "NFLX",
    "NFLX": "NFLX",
    "S&P": "^GSPC",
    "SPX": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW": "^DJI",
    "NIFTY 50": "^NSEI",
    "NIFTY": "^NSEI",
    "SENSEX": "^BSESN",
    "BSE SENSEX": "^BSESN",
    "DAX": "^GDAXI",
    "DAX 40": "^GDAXI",
    "NIKKEI": "^N225",
    "NIKKEI 225": "^N225",
    "HANG SENG": "^HSI",
    "HANGSENG": "^HSI",
    "HSI": "^HSI",
    "FTSE": "^FTSE",
    "FTSE 100": "^FTSE",
    "ASX 200": "^AXJO",
    "CAC 40": "^FCHI",
    "CAC40": "^FCHI",
    "VIX": "^VIX",
    "VOLATILITY": "^VIX",
    "GOLD": "GC=F",
    "SILVER": "SI=F",
    "SILICON": "^SOX",
    "SEMICONDUCTOR": "^SOX",
    "SMH": "SMH",
    "CRUDE": "CL=F",
    "OIL": "CL=F",
    "BRENT": "BZ=F",
    "NATURAL GAS": "NG=F",
    "COPPER": "HG=F",
    "PLATINUM": "PL=F",
    "DOLLAR INDEX": "DX-Y.NYB",
    "DXY": "DX-Y.NYB",
    "BOND": "^TYX",
    "TREASURY": "^TNX",
    "RUSSELL": "^RUT",
    "EURO STOXX": "^STOXX50E",
    "STOXX": "^STOXX50E",
}

COINGECKO_IDS = {
    "SOLANA": "solana",
    "SOL": "solana",
    "DOGE": "dogecoin",
    "DOGECOIN": "dogecoin",
    "XRP": "ripple",
    "RIPPLE": "ripple",
    "ADA": "cardano",
    "CARDANO": "cardano",
    "DOT": "polkadot",
    "POLKADOT": "polkadot",
    "AVAX": "avalanche-2",
    "AVALANCHE": "avalanche-2",
    "LINK": "chainlink",
    "CHAINLINK": "chainlink",
    "UNI": "uniswap",
    "UNISWAP": "uniswap",
    "MATIC": "matic-network",
    "POLYGON": "matic-network",
    "ATOM": "cosmos",
    "COSMOS": "cosmos",
    "LTC": "litecoin",
    "LITECOIN": "litecoin",
    "BCH": "bitcoin-cash",
    "TRX": "tron",
    "TRON": "tron",
    "NEAR": "near",
    "FTM": "fantom",
    "FANTOM": "fantom",
    "ARB": "arbitrum",
    "ARBITRUM": "arbitrum",
    "OP": "optimism",
    "OPTIMISM": "optimism",
    "APE": "apecoin",
    "APECOIN": "apecoin",
    "SAND": "the-sandbox",
    "MANA": "decentraland",
    "FIL": "filecoin",
    "FILECOIN": "filecoin",
    "THETA": "theta-token",
    "VET": "vechain",
    "VECHAIN": "vechain",
    "EOS": "eos",
    "ALGO": "algorand",
    "ALGORAND": "algorand",
    "ICP": "internet-computer",
    "RUNE": "thorchain",
    "AAVE": "aave",
    "CRV": "curve-dao-token",
    "MKR": "maker",
    "COMP": "compound-governance-token",
    "SUSHI": "sushi",
    "SUSHISWAP": "sushi",
    "CAKE": "pancakeswap-token",
    "KSM": "kusama",
    "KUSAMA": "kusama",
    "STX": "stacks",
    "STACKS": "stacks",
    "IMX": "immutable-x",
    "IMMUTABLE": "immutable-x",
    "EGLD": "elrond-erd-2",
    "HBAR": "hedera-hashgraph",
    "HEDERA": "hedera-hashgraph",
    "XLM": "stellar",
    "STELLAR": "stellar",
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





async def _try_coingecko_chart(query: str) -> dict | None:
    q = query.strip().upper()
    coin_id = None
    for keyword, cid in COINGECKO_IDS.items():
        if keyword in q:
            coin_id = cid
            break
    if not coin_id:
        return None

    try:
        import httpx
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"vs_currency": "usd", "days": "30"})
            if resp.status_code != 200:
                return None
            data = resp.json()
        prices = data.get("prices", [])
        if not prices:
            return None
        points = []
        for ts, price in prices:
            dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
            points.append({
                "date": dt.strftime("%Y-%m-%d"),
                "price": round(float(price), 2),
            })
        all_prices = [p["price"] for p in points]
        return {
            "label": coin_id.upper(),
            "unit": "USD",
            "current_price": all_prices[-1],
            "change_24h": "Live",
            "change_7d": "Live",
            "all_time_high": max(all_prices),
            "data": points,
        }
    except Exception:
        return None



async def _fetch_chart_data(query: str) -> dict | None:
    yf_task = asyncio.create_task(asyncio.to_thread(_try_yfinance_chart, query))
    cg_task = asyncio.create_task(_try_coingecko_chart(query))

    results = await asyncio.gather(yf_task, cg_task, return_exceptions=True)
    for result in results:
        if isinstance(result, dict) and result is not None:
            return result
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


async def _build_search_context(
    all_results: list[dict],
    browser_texts: dict[str, str] | None = None,
) -> str:
    search_context_lines = []
    if all_results:
        for i, r in enumerate(all_results[:8], 1):
            search_context_lines.append(f'{i}. "{r["title"]}"')
            search_context_lines.append(f'   URL: {r["url"]}')
            search_context_lines.append(f'   Source: {r.get("source", "web")}')
            search_context_lines.append(f'   Snippet: {r.get("snippet", "")}')
        search_context = "\n".join(search_context_lines)
        if browser_texts:
            for url, text in browser_texts.items():
                if text:
                    search_context += f"\n\nFULL ARTICLE TEXT (from {url}):\n{text[:3000]}"
    else:
        search_context = "No search results found."
    return search_context


async def _run_ai_analysis(
    query: str,
    search_context: str,
) -> dict:
    enriched_analysis = None
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Primary: AI/ML API
    if settings.AIML_API_ENABLED and settings.aiml_api_keys_list:
        try:
            from app.services.aiml_service import call_aiml

            aiml_user = FINANCIAL_USER_PROMPT.format(
                today=today_str,
                query=query,
                search_context_block=search_context,
            )
            raw = await call_aiml(FINANCIAL_SYSTEM_PROMPT, aiml_user, model=settings.AIML_FINANCIAL_MODEL, max_tokens=4096, timeout=120.0)
            enriched_analysis = parse_json_response(raw)
            enriched_analysis["_provider"] = "aiml"
            logger.info("Financial analysis completed via AI/ML API")
            return enriched_analysis
        except Exception as e:
            logger.warning(f"AIML financial analysis failed: {e}")

    if enriched_analysis is None:
        enriched_analysis = {
            "signal": "Neutral",
            "signal_strength": 0,
            "asset": "Unknown",
            "current_price": "N/A",
            "price_trend": "Sideways",
            "trend_magnitude": "Weak",
            "risk_level": "Medium",
            "risk_catalysts": [],
            "key_factors": [],
            "summary": "All AI providers exhausted.",
            "prediction_30d": {"bull_case": "N/A", "base_case": "N/A", "bear_case": "N/A"},
            "sources": [],
            "data_freshness": "stale",
            "_provider": "none",
        }

    return enriched_analysis


async def _enrich_with_wss(
    job_id: str,
    query: str,
    all_results: list[dict],
):
    """Phase 2 (background): extracts articles via WSS, re-runs AI, updates result."""
    try:
        await set_progress(job_id, "Extracting articles via browser...")

        top_urls = [r["url"] for r in all_results[:3] if r.get("url")]
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

        search_context = await _build_search_context(all_results, browser_texts)
        enriched_analysis = await _run_ai_analysis(query, search_context)

        graph_data = await _fetch_chart_data(query)

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
            "graph_data": graph_data,
            "analysis": enriched_analysis,
            "sources": sources,
            "enriching": False,
        }

        await update_financial_result(job_id, enriched_result)
        logger.info(f"WSS enrichment complete: {job_id}")

    except Exception as e:
        logger.error(f"WSS enrichment failed: {e}")
        try:
            saved = await get_saved_financial_result(job_id)
            if saved:
                r = saved.get("result")
                if isinstance(r, str):
                    r = json.loads(r)
                if isinstance(r, dict):
                    r["enriching"] = False
                    await update_financial_result(job_id, r)
        except Exception as e2:
            logger.error(f"Failed to clear enriching flag: {e2}")


async def process_financial_analysis(
    query_id: str,
    query: str,
    job_id: str,
):
    logger.info(f"Financial analysis started: {query}")

    try:
        await set_progress(job_id, "Searching Google, Bing & DuckDuckGo...")

        # Run SERP search in background
        serp_task = asyncio.create_task(_run_serp_search(query))

        # Phase 1: await SERP results — fast (~5s)
        all_results = await serp_task

        await set_progress(job_id, "Analyzing financial data...")

        # Fetch graph data from yfinance → CoinGecko → investing.com (parallel, returns first hit)
        graph_task = asyncio.create_task(_fetch_chart_data(query))

        # Build sources and run AI analysis on SERP snippets (parallel with graph)
        search_context = await _build_search_context(all_results)
        analysis_task = asyncio.create_task(_run_ai_analysis(query, search_context))
        graph_data = await graph_task

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

        # Wait for AI analysis
        analysis = await analysis_task

        result = {
            "mode": "financial",
            "status": STATUS_DONE,
            "jobId": job_id,
            "query": query,
            "graph_data": graph_data,
            "analysis": analysis,
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

        logger.info(f"Financial analysis complete (~10-15s): {job_id}")

        # Fire-and-forget WSS enrichment (improves AI context, runs in background)
        asyncio.create_task(_enrich_with_wss(job_id, query, all_results))

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
