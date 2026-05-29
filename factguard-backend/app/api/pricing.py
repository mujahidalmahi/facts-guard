import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
)

from app.exceptions import (
    ClaimNotFoundError,
)
from app.logging_config import (
    get_logger,
)
from app.schemas import (
    PriceCheckRequest,
)
from app.services.cache import (
    get_progress,
)
from app.services.dedup import dedup

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


@router.post("/cart")
async def cart(
    payload: PriceCheckRequest,
    background_tasks: BackgroundTasks,
):
    job_id = str(uuid.uuid4())

    logger.info(f"Starting cart check " f"(job_id: {job_id}, " f"product: {payload.product})")

    query_id = await create_query(
        payload.product,
        job_id,
    )

    background_tasks.add_task(
        process_price_check,
        query_id,
        payload.product,
        job_id,
    )

    return {"jobId": job_id}


# legacy compatibility
@router.post("/price-check")
async def price_check(
    payload: PriceCheckRequest,
    background_tasks: BackgroundTasks,
):
    return await cart(
        payload,
        background_tasks,
    )


@router.get("/price-result/{job_id}")
async def get_price_result(
    job_id: str,
):
    async def _fetch():
        data = await get_full_price_result(job_id)
        if not data:
            return None
        if data.get("status") == STATUS_PROCESSING:
            progress = await get_progress(job_id)
            return {"_progress": progress or PRICING_PROGRESS_SEARCHING}
        return data

    data = await dedup(f"price:{job_id}", _fetch)

    if data is None:
        raise ClaimNotFoundError(job_id)

    if progress := data.get("_progress"):
        return {
            "status": "processing",
            "jobId": job_id,
            "progress": progress,
        }

    return data
