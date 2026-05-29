import asyncio
import time
from typing import Any, Awaitable, Callable

from app.logging_config import get_logger

logger = get_logger("dedup")

_inflight: dict[str, asyncio.Future] = {}
_inflight_ttl: dict[str, float] = {}


async def dedup(
    key: str,
    factory: Callable[[], Awaitable[Any]],
    ttl: float = 2.0,
) -> Any:
    existing = _inflight.get(key)
    if existing is not None and not existing.done():
        logger.debug(f"Dedup hit for {key}")
        return await existing

    loop = asyncio.get_running_loop()
    future = loop.create_future()
    _inflight[key] = future

    try:
        result = await factory()
        if not future.done():
            future.set_result(result)
        return result
    except Exception as e:
        if not future.done():
            future.set_exception(e)
        raise
    finally:
        # Schedule cleanup without blocking the current coroutine
        async def _cleanup():
            await asyncio.sleep(ttl)
            _inflight.pop(key, None)
            _inflight_ttl.pop(key, None)

        _inflight_ttl[key] = time.monotonic() + ttl
        asyncio.ensure_future(_cleanup())
