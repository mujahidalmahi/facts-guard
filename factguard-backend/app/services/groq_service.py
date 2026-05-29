from openai import AsyncOpenAI

from app.config import settings
from app.logging_config import get_logger

logger = get_logger("groq")

_clients: list[AsyncOpenAI] | None = None


def _get_clients() -> list[AsyncOpenAI]:
    global _clients
    if _clients is None:
        raw = settings.GROQ_API_KEYS if settings.GROQ_API_KEYS else settings.GROQ_API_KEY
        keys = [k.strip() for k in raw.split(",") if k.strip()]
        if not keys:
            raise ValueError("No Groq API keys configured")
        _clients = [
            AsyncOpenAI(api_key=k, base_url="https://api.groq.com/openai/v1")
            for k in keys
        ]
    return _clients


async def call_groq(
    system: str,
    user: str,
    max_tokens: int = 1200,
    model: str = "llama-3.3-70b-versatile",
) -> str:
    clients = _get_clients()
    for i, client in enumerate(clients):
        try:
            resp = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                max_tokens=max_tokens,
            )
            text = resp.choices[0].message.content or ""
            logger.info(f"Groq response: {len(text)} chars (key_index={i})")
            return text
        except Exception as e:
            logger.warning(f"Groq key[{i}] failed: {e}")
            continue
    raise ValueError("All Groq API keys exhausted")
