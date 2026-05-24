"""
API v1 router configuration.
Includes all v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import verify, history

router = APIRouter()

# Include verification endpoints
router.include_router(
    verify.router,
    prefix="/verify",
    tags=["verification"],
)

# Include history endpoints
router.include_router(
    history.router,
    prefix="/history",
    tags=["history"],
)
