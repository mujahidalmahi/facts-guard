from openai import AsyncOpenAI

from app.config import settings
from app.logging_config import get_logger

logger = get_logger("groq")

_client = None


def _get_client() -> AsyncOpenAI | None:
    global _client
    if _client is None:
        key = settings.GROQ_API_KEY or ""
        if not key:
            logger.warning("GROQ_API_KEY not set")
            return None
        _client = AsyncOpenAI(
            api_key=key,
            base_url="https://api.groq.com/openai/v1",
        )
    return _client


async def call_groq(
    system: str,
    user: str,
    max_tokens: int = 1200,
    model: str = "llama-3.3-70b-versatile",
) -> str:
    client = _get_client()
    if client is None:
        raise ValueError("GROQ_API_KEY not configured")

    resp = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=max_tokens,
    )

    text = resp.choices[0].message.content or ""
    logger.info(f"Groq response: {len(text)} chars")
    return text
