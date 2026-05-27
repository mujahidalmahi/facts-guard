import asyncio
import uuid
from datetime import (
    datetime,
    timezone,
)

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Response,
)

from app.logging_config import (
    get_logger,
)

from app.schemas import (
    JobResponse,
    VerifyRequest,
)

from app.utils.constants import (
    STATUS_DONE,
    STATUS_ERROR,
)

from app.services.cache import (
    compute_claim_hash,
    get_cached_analysis,
    get_job_result,
    get_progress,
    push_claim_to_history,
    set_cached_analysis,
    set_job_result,
    set_progress,
)

from app.services.gemini import (
    analyze_claim,
)

from app.services.supabase_db import (
    create_claim,
    get_claim_by_job_id,
    get_result_by_job_id,
    save_result,
    save_sources,
    update_claim_status,
)

logger = get_logger("verify")

router = APIRouter()


PROCESS_TIMEOUT = 120


async def process_claim(
    claim_id: str,
    claim_text: str,
    job_id: str,
):
    try:
        await asyncio.wait_for(
            _process(claim_id, claim_text, job_id),
            timeout=PROCESS_TIMEOUT,
        )
    except asyncio.TimeoutError:
        logger.error(f"Claim processing timed out after {PROCESS_TIMEOUT}s")
        await set_progress(job_id, "Processing timed out")
        await update_claim_status(claim_id, STATUS_ERROR)
    except Exception as e:
        logger.error(f"Failed: {e}")
        await set_progress(job_id, "Failed")
        await update_claim_status(claim_id, STATUS_ERROR)


async def _process(
    claim_id: str,
    claim_text: str,
    job_id: str,
):
    try:
        await set_progress(
            job_id,
            "Checking cache...",
        )

        claim_hash = compute_claim_hash(claim_text)

        cached = await get_cached_analysis(claim_hash)

        if cached:
            result = cached

        else:
            result = await analyze_claim(
                claim_text,
                job_id,
            )

            if not result.pop(
                "_is_fallback",
                False,
            ):
                await set_cached_analysis(
                    claim_hash,
                    result,
                )

        await set_job_result(
            job_id,
            result,
        )

        await set_progress(
            job_id,
            "Saving results...",
        )

        result_id = await save_result(
            claim_id,
            result,
            job_id,
        )

        await save_sources(
            result_id,
            result.get(
                "sources",
                [],
            ),
        )

        await update_claim_status(
            claim_id,
            STATUS_DONE,
        )

        await push_claim_to_history(
            {
                "jobId": job_id,
                "claim": claim_text,
                "status": STATUS_DONE,
                "createdAt": datetime.now(timezone.utc).isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Failed: {e}")

        await set_progress(
            job_id,
            "Failed",
        )

        await update_claim_status(
            claim_id,
            STATUS_ERROR,
        )


@router.post("/verify", response_model=JobResponse, status_code=202)
async def verify(
    payload: VerifyRequest,
    background_tasks: BackgroundTasks,
):
    job_id = str(uuid.uuid4())

    claim_id = await create_claim(
        payload.claim,
        job_id,
    )

    background_tasks.add_task(
        process_claim,
        claim_id,
        payload.claim,
        job_id,
    )

    return JobResponse(jobId=job_id)


@router.get("/result/{job_id}")
async def get_result(
    job_id: str,
    response: Response,
):
    result = await get_job_result(job_id)

    if not result:
        db_row = await get_result_by_job_id(job_id)

        if db_row:
            result = db_row.get("raw_json")

    if result:
        response.headers["Cache-Control"] = "public, max-age=3600, stale-while-revalidate=86400"
        return {
            **result,
            "status": "done",
            "jobId": job_id,
        }

    claim = await get_claim_by_job_id(job_id)

    if claim and claim.get("status") == "error":
        return {
            "status": "error",
            "jobId": job_id,
        }

    progress = await get_progress(job_id)
    return {
        "status": "processing",
        "jobId": job_id,
        "progress": progress or "Initialising...",
    }
