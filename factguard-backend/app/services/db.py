import asyncio
import math
from typing import Any

from app.dependencies import get_supabase_service
from app.logging_config import get_logger

logger = get_logger("db")


def _sanitize(obj: Any) -> Any:
    """Recursively replace inf/-inf/NaN with None for JSON safety."""
    if isinstance(obj, float):
        if math.isinf(obj) or math.isnan(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in list(obj.items())}
    if isinstance(obj, list):
        return [_sanitize(v) for v in list(obj)]
    return obj


def _get_client():
    return get_supabase_service().get_client()


_CONNECTION_ERRORS = (
    "RemoteProtocolError",
    "ConnectionClosed",
    "ConnectError",
    "ReadTimeout",
    "WriteTimeout",
)


async def _db_call(callback):
    try:
        return await asyncio.to_thread(callback)
    except Exception as e:
        err_type = type(e).__name__
        logger.error(f"Database call failed: {err_type}: {e}")

        if any(conn_err in err_type for conn_err in _CONNECTION_ERRORS):
            logger.info("Recreating Supabase client and retrying...")
            try:
                get_supabase_service().reset_client()
                return await asyncio.to_thread(callback)
            except Exception as retry_e:
                retry_type = type(retry_e).__name__
                # The first call actually succeeded on the server if we get a
                # duplicate-key violation on retry (the row was already written).
                if retry_type == "APIError" and "23505" in str(retry_e):
                    logger.warning(f"Duplicate key on retry — first call succeeded: {retry_e}")
                    return None
                logger.error(f"Retry also failed: {retry_type}: {retry_e}")

        raise


async def insert(table: str, data: dict | list[dict]) -> Any:
    clean = _sanitize(data)
    return await _db_call(lambda: _get_client().table(table).insert(clean).execute())


async def update(table: str, data: dict, eq_field: str, eq_value: str) -> Any:
    clean = _sanitize(data)
    return await _db_call(
        lambda: _get_client().table(table).update(clean).eq(eq_field, eq_value).execute()
    )


async def select(
    table: str,
    fields: str = "*",
    eq_field: str | None = None,
    eq_value: str | None = None,
    maybe_single: bool = False,
    order: str | None = None,
    desc: bool = False,
    limit: int | None = None,
    offset: int | None = None,
    range_start: int | None = None,
    range_end: int | None = None,
) -> Any:
    def query():
        q = _get_client().table(table).select(fields)
        if eq_field and eq_value is not None:
            q = q.eq(eq_field, eq_value)
        if order:
            q = q.order(order, desc=desc)
        if limit is not None:
            q = q.limit(limit)
        if range_start is not None and range_end is not None:
            q = q.range(range_start, range_end)
        if offset is not None:
            q = q.offset(offset)
        if maybe_single:
            q = q.maybe_single()
        return q.execute()

    return await _db_call(query)
