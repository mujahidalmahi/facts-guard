import asyncio
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.cache import (
    compute_claim_hash,
    get_cached_analysis,
    push_claim_to_history,
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


async def process_claim(
    claim_id: str, claim_text: str, job_id: str
):
    try:
        claim_hash = compute_claim_hash(
            claim_text
        )
        cached = await get_cached_analysis(
            claim_hash
        )
        if cached:
            result = cached
        else:
            result = await analyze_claim(
                claim_text
            )
            await set_cached_analysis(
                claim_hash, result
            )

        result_id = await save_result(
            claim_id, result
        )

        await save_sources(
            result_id,
            result.get(
                "sources", []
            ),
        )

        await update_claim_status(
            claim_id, "done"
        )

        await push_claim_to_history({
            "jobId": job_id,
            "claim": claim_text,
            "status": "done",
            "createdAt": datetime.now(
                timezone.utc
            ).isoformat(),
        })
    except Exception:
        await update_claim_status(
            claim_id, "error"
        )


@router.post("/verify")
async def verify(
    payload: VerifyRequest
):
    job_id = str(uuid.uuid4())

    claim_id = await create_claim(
        payload.claim, job_id
    )

    asyncio.create_task(
        process_claim(
            claim_id, payload.claim, job_id
        )
    )

    return {
        "jobId": job_id,
    }


@router.get("/result/{job_id}")
async def get_result(
    job_id: str,
):
    data = await get_full_result(
        job_id
    )

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Result not found",
        )

    status = data.get("status")
    if status == "processing":
        return {"status": "processing"}

    return data