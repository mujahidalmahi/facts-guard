"""
Cache service for FactGuard API.
Handles caching of claim history and frequently accessed data.
"""

from typing import Optional
import asyncio
from app.logging_config import get_logger
from app.dependencies import get_supabase_service

logger = get_logger("cache")


async def get_cached_history(
    limit: int = 50,
    offset: int = 0,
) -> list[dict] | None:
    """
    Retrieve cached history of verified claims.
    
    Args:
        limit: Maximum number of claims to return (default: 50)
        offset: Number of claims to skip (for pagination)
        
    Returns:
        List of claim objects with their results, or None if query fails
        Each claim includes: jobId, claim, verdict, confidence, createdAt
    """
    try:
        logger.debug(
            f"Querying claim history (limit={limit}, offset={offset})"
        )
        
        # Get Supabase service from dependency
        supabase_service = get_supabase_service()
        client = supabase_service.get_client()
        
        # Run database query in thread to avoid blocking event loop
        def _query_claims():
            return (
                client.table("claims")
                .select(
                    "id, job_id, claim_text, created_at, "
                    "results(verdict, confidence, summary)"
                )
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
        
        response = await asyncio.to_thread(_query_claims)
        
        if not response.data:
            logger.info("No claim history found")
            return []
        
        # Transform response to match expected format
        claims = []
        for claim in response.data:
            result = claim.get("results")
            
            # Only include completed claims with results
            if result and isinstance(result, list) and len(result) > 0:
                result_data = result[0]
            elif result and isinstance(result, dict):
                result_data = result
            else:
                continue
            
            claims.append({
                "jobId": claim["job_id"],
                "claim": claim["claim_text"],
                "createdAt": claim["created_at"],
                "verdict": result_data.get("verdict", "Unknown"),
                "confidence": result_data.get("confidence", "Unknown"),
                "summary": result_data.get("summary", ""),
            })
        
        logger.info(
            f"Retrieved {len(claims)} claims from history "
            f"(limit={limit}, offset={offset})"
        )
        
        return claims
        
    except Exception as e:
        logger.error(f"Failed to retrieve claim history: {str(e)}")
        return None
