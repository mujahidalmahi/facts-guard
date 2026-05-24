import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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

    claim_id = create_claim(
        payload.claim, job_id
    )

    result = (
        await analyze_claim(
            payload.claim
        )
    )

    result_id = save_result(
        claim_id, result
    )

    save_sources(
        result_id,
        result.get("sources", []),
    )

    update_claim_status(
        claim_id, "done"
    )

    return {
        "jobId": job_id,
        "claim": payload.claim,
        "createdAt": datetime.now(
            timezone.utc
        ).isoformat(),
        **result,
    }


@router.get("/result/{job_id}")
async def get_result(
    job_id: str,
):
    data = get_full_result(job_id)
    if not data:
        raise HTTPException(
            status_code=404,
            detail="Result not found",
        )
    return data