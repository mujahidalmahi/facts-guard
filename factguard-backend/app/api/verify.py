import asyncio
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter

from app.exceptions import ClaimNotFoundError
from app.logging_config import get_logger
from app.schemas import VerifyRequest
from app.utils.constants import STATUS_DONE, STATUS_ERROR
from app.services.cache import (
    compute_claim_hash,
    get_cached_analysis,
    get_progress,
    push_claim_to_history,
    set_cached_analysis,
    set_progress,
)
from app.services.gemini import analyze_claim
from app.services.supabase_db import (
    create_claim,
    get_full_result,
    save_result,
    save_sources,
    update_claim_status,
)

logger = get_logger("verify")
router = APIRouter()


async def process_claim(claim_id: str, claim_text: str, job_id: str):
    try:
        await set_progress(job_id, "Checking cache...")

        claim_hash = compute_claim_hash(claim_text)
        cached = await get_cached_analysis(claim_hash)
        if cached:
            logger.info(f"Cache hit for claim hash: {claim_hash}")
            result = cached
        else:
            logger.info(f"Cache miss, analyzing claim: {claim_hash}")
            result = await analyze_claim(claim_text, job_id)
            if not result.pop("_is_fallback", False):
                await set_cached_analysis(claim_hash, result)

        await set_progress(job_id, "Saving results...")
        result_id = await save_result(claim_id, result)
        await save_sources(result_id, result.get("sources", []))
        await update_claim_status(claim_id, STATUS_DONE)

        await push_claim_to_history({
            "jobId": job_id,
            "claim": claim_text,
            "status": STATUS_DONE,
            "createdAt": datetime.now(timezone.utc).isoformat(),
        })
        logger.info(f"Claim {claim_id} processed successfully")
    except Exception as e:
        logger.error(f"Failed to process claim {claim_id}: {str(e)}")
        await set_progress(job_id, "Failed")
        await update_claim_status(claim_id, STATUS_ERROR)


@router.post("/verify")
async def verify(payload: VerifyRequest):
    job_id = str(uuid.uuid4())
    logger.info(f"Starting verification (job_id: {job_id})")

    claim_id = await create_claim(payload.claim, job_id)

    asyncio.create_task(
        process_claim(claim_id, payload.claim, job_id)
    )

    return {
        "jobId": job_id,
    }


@router.get("/result/{job_id}")
async def get_result(job_id: str):
    data = await get_full_result(job_id)

    if not data:
        raise ClaimNotFoundError(job_id)

    status = data.get("status")
    if status == "processing":
        progress = await get_progress(job_id)
        return {
            "status": "processing",
            "jobId": job_id,
            "progress": progress or "Processing...",
        }

    return data
