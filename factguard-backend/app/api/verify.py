import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.cache import (
    compute_claim_hash,
    get_cached_analysis,
    set_cached_analysis,
)
from app.services.gemini import (
    analyze_claim,
)

from app.services.supabase_db import (
    create_claim,
    get_full_result,
    save_result,
    save_sources,
    update_claim_status,
)

router = APIRouter()


class VerifyRequest(
    BaseModel
):
    claim: str


@router.post("/verify")
async def verify(
    payload: VerifyRequest
):
    job_id = str(uuid.uuid4())

    claim_id = await create_claim(
        payload.claim, job_id
    )

    claim_hash = compute_claim_hash(
        payload.claim
    )
    cached = await get_cached_analysis(
        claim_hash
    )
    if cached:
        result = cached
    else:
        result = await analyze_claim(
            payload.claim
        )
        await set_cached_analysis(
            claim_hash, result
        )

    result_id = await save_result(
        claim_id, result
    )

    await save_sources(
        result_id,
        result.get("sources", []),
    )

    await update_claim_status(
        claim_id, "done"
    )

    return {
        **result,
        "jobId": job_id,
        "claim": payload.claim,
        "createdAt": datetime.now(
            timezone.utc
        ).isoformat(),
    }


@router.get("/result/{job_id}")
async def get_result(
    job_id: str,
):
    data = await get_full_result(job_id)
    if not data:
        raise HTTPException(
            status_code=404,
            detail="Result not found",
        )
    return data