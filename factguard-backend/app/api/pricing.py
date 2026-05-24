import asyncio
import uuid

from fastapi import APIRouter

from app.exceptions import ClaimNotFoundError
from app.logging_config import get_logger
from app.schemas import PriceCheckRequest
from app.services.cache import get_progress
from app.services.pricing import (
    create_query,
    get_full_price_result,
    process_price_check,
)
from app.utils.constants import (
    PRICING_PROGRESS_SEARCHING,
    STATUS_PROCESSING,
)

logger = get_logger("pricing")
router = APIRouter()


@router.post("/price-check")
async def price_check(payload: PriceCheckRequest):
    job_id = str(uuid.uuid4())
    logger.info(f"Starting price check (job_id: {job_id}, product: {payload.product})")

    query_id = await create_query(payload.product, job_id)

    asyncio.create_task(
        process_price_check(query_id, payload.product, job_id)
    )

    return {
        "jobId": job_id,
    }


@router.get("/price-result/{job_id}")
async def get_price_result(job_id: str):
    data = await get_full_price_result(job_id)

    if not data:
        raise ClaimNotFoundError(job_id)

    status = data.get("status")
    if status == STATUS_PROCESSING:
        progress = await get_progress(job_id)
        return {
            "status": "processing",
            "jobId": job_id,
            "progress": progress or PRICING_PROGRESS_SEARCHING,
        }

    return data
