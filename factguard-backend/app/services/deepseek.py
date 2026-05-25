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

client = OpenAI(
    api_key=
        settings.DEEPSEEK_API_KEY,
    base_url=
        "https://openrouter.ai/api/v1",
)


async def deepseek_financial_analysis(
    query: str,
    market_context: str,
) -> dict:
    try:
        prompt = f"""
You are a financial AI analyst.

Analyze:

{query}

Market Data:
{market_context}

Return ONLY JSON.

{{
  "signal": "BUY | SELL | HOLD",
  "signal_strength": "Weak | Moderate | Strong",
  "price_trend": "Bullish | Bearish | Sideways",
  "summary": "short explanation",
  "risk_level": "Low | Medium | High",
  "prediction_30d": "brief prediction",
  "confidence": "Low | Medium | High",
  "key_factors": [
    "factor 1",
    "factor 2"
  ]
}}
"""

        response = (
            client.chat.completions.create(
                model=
                    "deepseek/deepseek-chat-v3",
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