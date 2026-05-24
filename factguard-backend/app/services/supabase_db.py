from typing import Any

from app.dependencies import get_supabase_service
from app.logging_config import get_logger
from app.utils.constants import STATUS_PROCESSING

logger = get_logger("supabase_db")


def _get_client():
    return get_supabase_service().get_client()


async def _db_call(callback):
    import asyncio
    return await asyncio.to_thread(callback)


async def _insert(table: str, data: dict | list[dict]) -> Any:
    return await _db_call(lambda: _get_client().table(table).insert(data).execute())


async def _update(table: str, data: dict, eq_field: str, eq_value: str) -> Any:
    return await _db_call(
        lambda: _get_client().table(table).update(data).eq(eq_field, eq_value).execute()
    )


async def _select(table: str, fields: str = "*", eq_field: str | None = None, eq_value: str | None = None,
                  maybe_single: bool = False, order: str | None = None, desc: bool = False,
                  limit: int | None = None, offset: int | None = None, range_start: int | None = None,
                  range_end: int | None = None) -> Any:
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


def _source_to_insert(s: dict, result_id: str) -> dict:
    return {
        "result_id": result_id,
        "url": s.get("url", ""),
        "title": s.get("title", ""),
        "author": s.get("author"),
        "published": s.get("date"),
        "stance": s.get("stance", "neutral"),
        "relevance": s.get("relevance", 5),
        "summary": s.get("summary", ""),
        "quote": s.get("quote"),
    }


def _source_to_response(s: Any) -> dict:
    return {
        "url": s["url"],
        "title": s["title"],
        "author": s.get("author"),
        "date": s.get("published"),
        "stance": s["stance"],
        "relevance": s.get("relevance", 5),
        "summary": s.get("summary", ""),
        "quote": s.get("quote"),
    }


async def create_claim(claim_text: str, job_id: str) -> str:
    result = await _insert("claims", {
        "claim_text": claim_text,
        "job_id": job_id,
        "status": STATUS_PROCESSING,
    })
    claim_id = result.data[0]["id"]
    logger.debug(f"Claim created: {claim_id}")
    return claim_id


async def save_result(claim_id: str, data: dict[str, Any]) -> str:
    result = await _insert("results", {
        "claim_id": claim_id,
        "verdict": data["verdict"],
        "confidence": data["confidence"],
        "summary": data["summary"],
        "supports": data.get("supports", 0),
        "contradicts": data.get("contradicts", 0),
        "neutral": data.get("neutral", 0),
    })
    result_id = result.data[0]["id"]
    logger.debug(f"Result saved: {result_id}")
    return result_id


async def save_sources(result_id: str, sources: list[dict[str, Any]]):
    if not sources:
        logger.debug("No sources to save")
        return
    rows = [_source_to_insert(s, result_id) for s in sources]
    await _insert("sources", rows)
    logger.debug(f"Saved {len(rows)} sources")


async def update_claim_status(claim_id: str, status: str):
    await _update("claims", {"status": status}, "id", claim_id)
    logger.debug(f"Claim {claim_id} status updated to: {status}")


async def get_full_result(job_id: str) -> dict[str, Any] | None:
    claim_response = await _select("claims", eq_field="job_id", eq_value=job_id, maybe_single=True)
    if not claim_response.data:
        logger.warning(f"Claim not found for job_id: {job_id}")
        return None

    claim = claim_response.data
    claim_id = claim["id"]
    status = claim["status"]

    result_response = await _select("results", eq_field="claim_id", eq_value=claim_id, maybe_single=True)
    if not result_response.data:
        logger.debug(f"Result not yet available for claim: {claim_id}")
        return {
            "status": status,
            "jobId": claim["job_id"],
            "claim": claim["claim_text"],
            "createdAt": claim["created_at"],
        }

    result = result_response.data
    sources_response = await _select("sources", eq_field="result_id", eq_value=result["id"])
    sources_data = sources_response.data or []

    logger.debug(f"Full result retrieved for job_id: {job_id}")

    return {
        "status": status,
        "jobId": claim["job_id"],
        "claim": claim["claim_text"],
        "createdAt": claim["created_at"],
        "verdict": result["verdict"],
        "confidence": result["confidence"],
        "summary": result["summary"],
        "supports": result["supports"],
        "contradicts": result["contradicts"],
        "neutral": result["neutral"],
        "sources": [_source_to_response(s) for s in sources_data],
    }


async def list_claims() -> list[dict[str, Any]]:
    claims_response = await _select(
        "claims",
        fields="id, job_id, claim_text, status, created_at",
        order="created_at",
        desc=True,
        limit=50,
    )
    return [
        {
            "jobId": c["job_id"],
            "claim": c["claim_text"],
            "status": c["status"],
            "createdAt": c["created_at"],
        }
        for c in claims_response.data
    ]


async def get_recent_results(limit: int = 10, offset: int = 0) -> list[dict[str, Any]]:
    response = await _select(
        "claims",
        eq_field="status",
        eq_value="done",
        order="created_at",
        desc=True,
        range_start=offset,
        range_end=offset + limit - 1,
    )
    return response.data or []
