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
    FinancialRequest,
)

from app.services.cache import (
    get_progress,
)
from app.services.dedup import dedup

from app.services.financial import (
    create_financial_query,
    process_financial_analysis,
    get_full_financial_result,
)

from app.utils.constants import (
    STATUS_PROCESSING,
)

logger = get_logger("financial")

router = APIRouter()


@router.post("/financial")
async def financial(
    payload: FinancialRequest,
    background_tasks: BackgroundTasks,
):
    job_id = str(uuid.uuid4())

    logger.info(f"Starting financial analysis " f"(job_id={job_id}, " f"query={payload.query})")

    query_id = await create_financial_query(
        payload.query,
        job_id,
    )

    background_tasks.add_task(
        process_financial_analysis,
        query_id,
        payload.query,
        job_id,
    )

    return {"jobId": job_id}


@router.get("/financial-result/{job_id}")
async def get_financial_result(
    job_id: str,
):
    async def _fetch():
        data = await get_full_financial_result(job_id)
        if not data:
            return None
        if data.get("status") == STATUS_PROCESSING:
            progress = await get_progress(job_id)
            return {"_progress": progress or "Fetching market data..."}
        return data

    data = await dedup(f"financial:{job_id}", _fetch)

    if data is None:
        raise ClaimNotFoundError(job_id)

    if progress := data.get("_progress"):
        return {
            "status": "processing",
            "jobId": job_id,
            "progress": progress,
        }

    return data
