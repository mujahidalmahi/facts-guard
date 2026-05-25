from openai import (
    OpenAI,
)

from app.config import (
    settings,
)

from app.logging_config import (
    get_logger,
)

logger = get_logger(
    "deepseek"
)

_client = None

def _get_client():
    global _client
    if _client is None:
        key = settings.DEEPSEEK_API_KEY
        if not key:
            raise ValueError("DEEPSEEK_API_KEY not configured")
        _client = OpenAI(
            api_key=key,
            base_url="https://openrouter.ai/api/v1",
        )
    return _client


async def deepseek_financial_analysis(
    query: str,
    context: str,
) -> dict:
    try:
        prompt = f"""
You are a financial AI analyst. Use the live web search results below to answer the user's query.

User Query: {query}

Web Search Results:
{context or "No web search results available. Use your best judgment."}

Return ONLY valid JSON with these fields:
- "signal": "BUY" | "SELL" | "HOLD"
- "signal_strength": "Weak" | "Moderate" | "Strong"
- "price_trend": "Bullish" | "Bearish" | "Sideways"
- "summary": 2-3 sentence explanation with specific data from search results
- "risk_level": "Low" | "Medium" | "High"
- "prediction_30d": brief outlook
- "confidence": "Low" | "Medium" | "High"
- "key_factors": list of 2-4 key factors

Do NOT wrap in markdown. Return raw JSON only.
"""

        response = (
            _get_client().chat.completions.create(
                model=
                    "deepseek/deepseek-v4-flash:free",
                messages=[
                    {
                        "role":
                            "user",
                        "content":
                            prompt,
                    }
                ],
                temperature=0.3,
            )
        )

        text = (
            response
            .choices[0]
            .message.content
        )

        import json

        return json.loads(
            text
        )

    except Exception as e:
        logger.error(
            f"DeepSeek failed: {e}"
        )

        return {
            "signal":
                "HOLD",
            "signal_strength":
                "Moderate",
            "price_trend":
                "Sideways",
            "summary":
                "Analysis unavailable.",
            "risk_level":
                "Medium",
            "prediction_30d":
                "Uncertain",
            "confidence":
                "Low",
            "key_factors":
                [],
        }