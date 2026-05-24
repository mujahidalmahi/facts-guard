"""
API v1 router configuration.
Includes all v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import verify

router = APIRouter()

# Include verification endpoints
router.include_router(
    verify.router,
    prefix="/verify",
    tags=["verification"],
)
