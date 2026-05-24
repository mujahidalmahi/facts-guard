import asyncio
from typing import Any

from app.dependencies import get_supabase_service
from app.logging_config import get_logger

logger = get_logger("db")


def _get_client():
    return get_supabase_service().get_client()


async def _db_call(callback):
    try:
        return await asyncio.to_thread(callback)
    except Exception as e:
        logger.error(f"Database call failed: {type(e).__name__}: {e}")
        raise


async def insert(table: str, data: dict | list[dict]) -> Any:
    return await _db_call(lambda: _get_client().table(table).insert(data).execute())


async def update(table: str, data: dict, eq_field: str, eq_value: str) -> Any:
    return await _db_call(
        lambda: _get_client().table(table).update(data).eq(eq_field, eq_value).execute()
    )


async def select(
    table: str, fields: str = "*",
    eq_field: str | None = None, eq_value: str | None = None,
    maybe_single: bool = False, order: str | None = None, desc: bool = False,
    limit: int | None = None, offset: int | None = None,
    range_start: int | None = None, range_end: int | None = None,
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
