"""
Claim history endpoints for FactGuard API v1.
Handles retrieval of verification history.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Optional

from app.logging_config import get_logger
from app.services.cache import get_cached_history

logger = get_logger("history_endpoint")

router = APIRouter()


class HistoryClaimItem(BaseModel):
    """Single claim item in history."""
    
    jobId: str = Field(..., description="Unique job ID for tracking")
    claim: str = Field(..., description="The original claim")
    createdAt: str = Field(..., description="ISO-8601 timestamp")
    verdict: str = Field(..., description="Analysis verdict")
    confidence: str = Field(..., description="Confidence level")
    summary: str = Field(..., description="Brief summary of analysis")
    
    class Config:
        # Allow both snake_case and camelCase for Pydantic v2
        populate_by_name = True


class HistoryResponse(BaseModel):
    """Response schema for history endpoint."""
    
    claims: list[HistoryClaimItem] = Field(
        default_factory=list,
        description="List of verified claims"
    )
    total: int = Field(
        ...,
        description="Total number of claims in system"
    )


@router.get(
    "",
    response_model=HistoryResponse,
    summary="Get claim verification history",
    description="Retrieve a paginated list of previously verified claims",
)
async def history(
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of claims to return"
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of claims to skip (for pagination)"
    ),
) -> HistoryResponse:
    """
    Retrieve the history of verified claims.
    
    Args:
        limit: Maximum number of claims to return (1-100, default 50)
        offset: Number of claims to skip for pagination (default 0)
        
    Returns:
        HistoryResponse with list of claims and total count
    """
    logger.info(
        f"Retrieving claim history (limit={limit}, offset={offset})"
    )
    
    try:
        claims_data = await get_cached_history(limit=limit, offset=offset)
        
        if claims_data is None:
            logger.warning("Failed to retrieve history, returning empty list")
            claims_data = []
        
        # Convert to HistoryClaimItem objects
        claims = [
            HistoryClaimItem(
                jobId=c["jobId"],
                claim=c["claim"],
                createdAt=c["createdAt"],
                verdict=c["verdict"],
                confidence=c["confidence"],
                summary=c["summary"],
            )
            for c in claims_data
        ]
        
        logger.info(f"Successfully retrieved {len(claims)} claims from history")
        
        return HistoryResponse(
            claims=claims,
            total=len(claims)
        )
        
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        return HistoryResponse(
            claims=[],
            total=0
        )
