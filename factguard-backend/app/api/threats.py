import uuid

from fastapi import APIRouter

from app.logging_config import get_logger
from app.services.threat_monitor import (
    scan_for_threats,
    generate_compliance_report,
)

logger = get_logger("threats_api")

router = APIRouter(
    prefix="/threats",
    tags=["threats"],
)


@router.get("/scan")
@router.post("/scan")
async def scan_threats(query: str | None = None):
    """Scan news sources for potential threats."""
    threats = await scan_for_threats(query=query)
    return {
        "jobId": str(uuid.uuid4()),
        "threats": threats,
        "count": len(threats),
    }


@router.get("/report")
async def compliance_report(query: str | None = None):
    """Generate a compliance report from current threat scan."""
    threats = await scan_for_threats(query=query)
    report = await generate_compliance_report(threats)
    return {
        "report": report,
        "threats": threats,
        "count": len(threats),
    }
