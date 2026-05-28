import asyncio
import json
from datetime import (
    datetime,
    timezone,
)

from openai import (
    OpenAI,
)

from app.config import (
    settings,
)

from app.logging_config import (
    get_logger,
)

logger = get_logger("deepseek")

api_keys: list[str] = []


def _get_api_keys() -> list[str]:
    global api_keys

    if not api_keys:
        api_keys = list(settings.deepseek_api_keys_list)

        if not api_keys:
            raise ValueError("DEEPSEEK_API_KEYS not configured")

    return api_keys


def _get_client(
    api_key: str,
) -> OpenAI:
    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
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


FALLBACK_RESPONSE = {
    "signal": "Neutral",
    "signal_strength": 0,
    "asset": "Unknown",
    "current_price": "N/A",
    "price_trend": "Sideways",
    "trend_magnitude": "Weak",
    "risk_level": "Medium",
    "risk_catalysts": [],
    "key_factors": [],
    "summary": "Analysis unavailable.",
    "prediction_30d": {
        "bull_case": "N/A",
        "base_case": "N/A",
        "bear_case": "N/A",
    },
    "sources": [],
    "data_freshness": "stale",
}


def build_search_context(results: list[dict]) -> str:
    if not results:
        return "(No search results available)"
    lines = []
    for i, r in enumerate(results, 1):
        snippet = r.get("snippet", "")
        if len(snippet) > 200:
            snippet = snippet[:200] + "..."
        lines += [
            f"[{i}] Title: {r['title']}",
            f"    URL: {r['url']}",
            f"    Snippet: {snippet}",
            "",
        ]
    return "\n".join(lines)


async def deepseek_financial_analysis(
    query: str,
    context: str,
) -> dict:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if isinstance(context, str) and context.startswith("["):
        try:
            context = build_search_context(json.loads(context))
        except json.JSONDecodeError:
            pass

    user_prompt = FINANCIAL_USER_PROMPT.format(
        today=today,
        query=query,
        search_context_block=context or "(No search results available)",
    )

    keys = _get_api_keys()

    for attempt, key in enumerate(keys):
        try:
            logger.info(f"DeepSeek attempt {attempt + 1}/{len(keys)}")

            client = _get_client(key)

            response = client.chat.completions.create(
                model=settings.FINANCIAL_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": FINANCIAL_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=0.2,
            )

            text = response.choices[0].message.content

            result = json.loads(text)

            result["analysis_date"] = result.get(
                "analysis_date",
                today,
            )

            return result

        except Exception as e:
            logger.error(f"DeepSeek attempt {attempt + 1} failed: {e}")

            continue

    logger.error("All DeepSeek API keys exhausted")

    fallback = dict(FALLBACK_RESPONSE)
    fallback["analysis_date"] = today
    return fallback


async def call_deepseek(
    system: str,
    user: str,
    max_tokens: int = 4096,
    model: str | None = None,
) -> str:
    """Generic DeepSeek/OpenRouter call for fallback scenarios.

    Returns raw text response, similar to call_groq().
    Raises ValueError if all keys exhausted.
    """
    keys = _get_api_keys()
    resolved_model = model or settings.FINANCIAL_MODEL

    for attempt, key in enumerate(keys):
        try:
            client = _get_client(key)
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=resolved_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                max_tokens=max_tokens,
                temperature=0.2,
            )
            text = response.choices[0].message.content or ""
            logger.info(f"DeepSeek call: {len(text)} chars (attempt {attempt + 1})")
            return text

        except Exception as e:
            logger.error(f"DeepSeek attempt {attempt + 1} failed: {e}")
            continue

    raise ValueError("All DeepSeek API keys exhausted")
