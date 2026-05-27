from typing import Any

from app.exceptions import DatabaseError
from app.logging_config import get_logger
from app.services.db import insert, select, update
from app.utils.constants import STATUS_PROCESSING

logger = get_logger("supabase_db")


def _source_toinsert(s: dict, result_id: str) -> dict:
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
        "credibility": s.get("credibility"),
    }


def _source_to_response(s: Any) -> dict:
    return {
        "url": s.get("url", ""),
        "title": s.get("title", ""),
        "author": s.get("author"),
        "date": s.get("published"),
        "stance": s.get("stance", "neutral"),
        "relevance": s.get("relevance", 5),
        "summary": s.get("summary", ""),
        "quote": s.get("quote"),
        "credibility": s.get("credibility"),
    }


async def create_claim(claim_text: str, job_id: str) -> str:
    try:
        result = await insert(
            "claims",
            {
                "claim_text": claim_text,
                "job_id": job_id,
                "status": STATUS_PROCESSING,
            },
        )
        if not result or not result.data:
            raise ValueError("No data returned from database")
        claim_id = result.data[0]["id"]
        logger.debug(f"Claim created: {claim_id}")
        return claim_id
    except Exception as e:
        logger.error(f"Failed to create claim: {type(e).__name__}: {e}")
        raise DatabaseError(f"Failed to create claim: {e}")


async def save_result(claim_id: str, data: dict[str, Any], job_id: str | None = None) -> str:
    try:
        insert_data = {
            "claim_id": claim_id,
            "verdict": data.get("verdict", "Unverified"),
            "confidence": data.get("confidence", "Low"),
            "summary": data.get("summary", ""),
            "supports": data.get("supports", 0),
            "contradicts": data.get("contradicts", 0),
            "neutral": data.get("neutral", 0),
            "raw_json": data,
        }
        if job_id:
            insert_data["job_id"] = job_id
        result = await insert("results", insert_data)
        if not result or not result.data:
            raise ValueError("No data returned from database")
        result_id = result.data[0]["id"]
        logger.debug(f"Result saved: {result_id}")
        return result_id
    except Exception as e:
        logger.error(f"Failed to save result: {type(e).__name__}: {e}")
        raise DatabaseError(f"Failed to save result: {e}")


async def save_sources(result_id: str, sources: list[dict[str, Any]]):
    if not sources:
        logger.debug("No sources to save")
        return
    rows = [_source_toinsert(s, result_id) for s in sources]
    await insert("sources", rows)
    logger.debug(f"Saved {len(rows)} sources")


async def update_claim_status(claim_id: str, status: str):
    await update("claims", {"status": status}, "id", claim_id)
    logger.debug(f"Claim {claim_id} status updated to: {status}")


async def get_full_result(job_id: str) -> dict[str, Any] | None:
    try:
        claim_response = await select(
            "claims", eq_field="job_id", eq_value=job_id, maybe_single=True
        )
    except Exception as e:
        logger.error(f"Failed to query claim for job_id {job_id}: {type(e).__name__}: {e}")
        return None

    if not claim_response or not claim_response.data:
        logger.warning(f"Claim not found for job_id: {job_id}")
        return None

    claim = claim_response.data
    claim_id = claim.get("id")
    if not claim_id:
        logger.warning(f"Claim has no id for job_id: {job_id}")
        return None

    status = claim.get("status", "processing")

    try:
        result_response = await select(
            "results", eq_field="claim_id", eq_value=claim_id, maybe_single=True
        )
    except Exception as e:
        logger.error(f"Failed to query result for claim {claim_id}: {type(e).__name__}: {e}")
        return None

    if not result_response or not result_response.data:
        logger.debug(f"Result not yet available for claim: {claim_id}")
        return {
            "status": status,
            "jobId": claim.get("job_id", job_id),
            "claim": claim.get("claim_text", ""),
            "createdAt": claim.get("created_at"),
        }

    result = result_response.data
    try:
        sources_response = await select("sources", eq_field="result_id", eq_value=result["id"])
    except Exception as e:
        logger.error(f"Failed to query sources for result {result['id']}: {type(e).__name__}: {e}")
        sources_data = []
    else:
        sources_data = sources_response.data or []

    logger.debug(f"Full result retrieved for job_id: {job_id}")

    return {
        "status": status,
        "jobId": claim.get("job_id", job_id),
        "claim": claim.get("claim_text", ""),
        "createdAt": claim.get("created_at"),
        "verdict": result.get("verdict", "Unverified"),
        "confidence": result.get("confidence", "Low"),
        "summary": result.get("summary", ""),
        "supports": result.get("supports", 0),
        "contradicts": result.get("contradicts", 0),
        "neutral": result.get("neutral", 0),
        "sources": [_source_to_response(s) for s in sources_data],
    }


async def get_result_by_job_id(job_id: str) -> dict | None:
    try:
        response = await select(
            "results",
            eq_field="job_id",
            eq_value=job_id,
            limit=1,
        )
        if response and response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        logger.warning(f"get_result_by_job_id({job_id}): {e}")
        return None


async def get_claim_by_job_id(job_id: str) -> dict | None:
    try:
        response = await select(
            "claims",
            eq_field="job_id",
            eq_value=job_id,
            limit=1,
        )
        if response and response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        logger.warning(f"get_claim_by_job_id({job_id}): {e}")
        return None


async def list_claims() -> list[dict[str, Any]]:
    claims_response = await select(
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
    response = await select(
        "claims",
        eq_field="status",
        eq_value="done",
        order="created_at",
        desc=True,
        range_start=offset,
        range_end=offset + limit - 1,
    )
    return response.data or []


# -------------------------
# Financial Persistence
# -------------------------


async def save_financial_result(
    job_id: str,
    query: str,
    data: dict[str, Any],
):
    try:
        await insert(
            "financial_results",
            {
                "job_id": job_id,
                "query": query,
                "result": data,
            },
        )

        logger.debug(f"Financial result saved: {job_id}")

    except Exception as e:
        logger.error(f"Failed to save financial result: {e}")


async def get_saved_financial_result(
    job_id: str,
) -> dict[str, Any] | None:
    try:
        response = await select(
            "financial_results",
            eq_field="job_id",
            eq_value=job_id,
            maybe_single=True,
        )

        return response.data if response else None

    except Exception as e:
        logger.error(f"Financial fetch failed: {e}")

        return None


# -------------------------
# Cart Persistence
# -------------------------


async def save_cart_result(
    job_id: str,
    product: str,
    data: dict[str, Any],
):
    try:
        await insert(
            "cart_results",
            {
                "job_id": job_id,
                "product": product,
                "result": data,
            },
        )

        logger.debug(f"Cart result saved: {job_id}")

    except Exception as e:
        logger.error(f"Failed to save cart result: {e}")


async def get_saved_cart_result(
    job_id: str,
) -> dict[str, Any] | None:
    try:
        response = await select(
            "cart_results",
            eq_field="job_id",
            eq_value=job_id,
            maybe_single=True,
        )

        return response.data if response else None

    except Exception as e:
        logger.error(f"Cart fetch failed: {e}")

        return None
