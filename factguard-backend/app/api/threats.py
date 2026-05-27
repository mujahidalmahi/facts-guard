import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field

from app.exceptions import ClaimNotFoundError
from app.logging_config import get_logger
from app.services.cache import get_job_result, get_progress, set_job_result, set_progress, push_claim_to_history
from app.services.threat_monitor import scan_for_threats, generate_compliance_report
from app.utils.constants import STATUS_PROCESSING

logger = get_logger("threats_api")

router = APIRouter(
    prefix="/threats",
    tags=["threats"],
)


class ThreatScanRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)


async def process_threat_scan(query: str, job_id: str) -> None:
    try:
        await set_progress(job_id, "Scanning domains for threats...")

        threats = await scan_for_threats(query=query)

        await set_progress(job_id, "Generating compliance report...")
        report = await generate_compliance_report(threats)

        result = {
            "jobId": job_id,
            "threats": threats,
            "report": report,
            "status": "done",
        }

        await set_job_result(job_id, result)

        await push_claim_to_history({
            "jobId": job_id,
            "claim": query,
            "mode": "security",
            "status": "done",
            "verdict": threats[0].get("severity", "unknown") if threats else "clear",
            "createdAt": datetime.now(timezone.utc).isoformat(),
        })
    except Exception as e:
        logger.error(f"Threat scan failed for job {job_id}: {e}")
        await set_job_result(job_id, {"status": "error", "jobId": job_id, "error": str(e)})


@router.post("/scan")
async def scan_threats(payload: ThreatScanRequest, background_tasks: BackgroundTasks):
    """Scan news sources for potential threats (async with job tracking)."""
    job_id = str(uuid.uuid4())
    logger.info(f"Starting threat scan (job_id={job_id}, query={payload.query})")

    background_tasks.add_task(process_threat_scan, payload.query, job_id)

    return {"jobId": job_id}


@router.get("/result/{job_id}")
async def get_threat_result(job_id: str):
    """Poll for threat scan result."""
    data = await get_job_result(job_id)

    if not data:
        raise ClaimNotFoundError(job_id)

    status = data.get("status")

    if status == STATUS_PROCESSING or not status or status == "processing":
        progress = await get_progress(job_id)
        return {
            "status": "processing",
            "jobId": job_id,
            "progress": progress or "Scanning for threats...",
        }

    return data


@router.get("/report")
async def compliance_report(query: str | None = None):
    """Generate a compliance report from current threat scan (synchronous)."""
    threats = await scan_for_threats(query=query)
    report = await generate_compliance_report(threats)
    return {
        "report": report,
        "threats": threats,
        "count": len(threats),
    }
