import asyncio

import openai
from openai import AsyncOpenAI

from app.config import settings
from app.logging_config import get_logger

logger = get_logger("aiml_service")

_key_exhausted: dict[int, bool] = {0: False, 1: False}
_EXHAUSTED_TTL = 3600


def _get_keys() -> list[str]:
    raw = settings.AIML_API_KEYS
    keys = [k.strip() for k in raw.split(",") if k.strip()]
    if not keys:
        raise ValueError("AIML_API_KEYS not configured")
    return keys


def _make_client(api_key: str) -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.aimlapi.com/v1",
        timeout=30.0,
        max_retries=0,
    )


async def _mark_key_exhausted(key_index: int) -> None:
    _key_exhausted[key_index] = True
    try:
        from app.services.cache import _get_client as _redis_client
        redis = await _redis_client()
        if redis:
            await redis.setex(
                f"factguard:aiml:exhausted:{key_index}",
                _EXHAUSTED_TTL,
                "1",
            )
    except Exception:
        pass


async def _is_key_exhausted(key_index: int) -> bool:
    try:
        from app.services.cache import _get_client as _redis_client
        redis = await _redis_client()
        if redis:
            val = await redis.get(f"factguard:aiml:exhausted:{key_index}")
            return val is not None
    except Exception:
        pass
    return _key_exhausted.get(key_index, False)


async def call_aiml(
    system: str,
    user: str,
    model: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.2,
) -> str:
    keys = _get_keys()
    resolved_model = model or settings.AIML_API_MODEL

    for key_index, api_key in enumerate(keys):
        if await _is_key_exhausted(key_index):
            logger.info(f"AIML key[{key_index}] is marked exhausted — skipping")
            continue

        client = _make_client(api_key)
        try:
            logger.info(f"AIML call: model={resolved_model}, key_index={key_index}")
            response = await client.chat.completions.create(
                model=resolved_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            text = response.choices[0].message.content or ""
            logger.info(f"AIML success: {len(text)} chars (key_index={key_index})")
            return text

        except openai.RateLimitError:
            logger.warning(f"AIML key[{key_index}] quota exhausted — rotating to next key")
            await _mark_key_exhausted(key_index)
            continue

        except (openai.APIStatusError, openai.APIConnectionError) as e:
            status = getattr(e, "status_code", None)
            if status == 401:
                logger.error(f"AIML key[{key_index}] is invalid (401) — skipping")
                await _mark_key_exhausted(key_index)
                continue
            logger.warning(f"AIML key[{key_index}] transient error ({status}): {e} — retrying once")
            try:
                response = await client.chat.completions.create(
                    model=resolved_model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                text = response.choices[0].message.content or ""
                logger.info(f"AIML retry success: {len(text)} chars (key_index={key_index})")
                return text
            except Exception as retry_err:
                logger.warning(f"AIML key[{key_index}] retry failed: {retry_err} — trying next key")
                continue

        except asyncio.TimeoutError:
            logger.warning(f"AIML key[{key_index}] timed out — trying next key")
            continue

        except Exception as e:
            logger.error(f"AIML key[{key_index}] unexpected error: {e} — trying next key")
            continue

    raise ValueError("All AIML API keys exhausted or invalid")


async def get_aiml_key_status() -> dict:
    keys = _get_keys()
    status = {}
    for i, _ in enumerate(keys):
        exhausted = await _is_key_exhausted(i)
        status[f"key_{i}"] = {
            "index": i,
            "exhausted": exhausted,
            "label": f"KEY_{i + 1}",
        }
    return status
