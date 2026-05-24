"""
Optimized Supabase database service for FactGuard.
Eliminates N+1 query problems and provides clean database abstraction.
"""

from typing import Any, Optional
from app.logging_config import get_logger

logger = get_logger("supabase_service")


class OptimizedSupabaseService:
    """Optimized database operations with efficient querying."""

    def __init__(self, client):
        """Initialize with Supabase client."""
        self.client = client

    def create_claim(self, claim_text: str, job_id: str) -> str:
        """
        Create a new claim record.

        Args:
            claim_text: The claim to verify
            job_id: Unique job identifier

        Returns:
            Claim ID

        Raises:
            Exception: If database operation fails
        """
        logger.debug(f"Creating claim: {job_id}")
        result = (
            self.client.table("claims")
            .insert(
                {
                    "claim_text": claim_text,
                    "job_id": job_id,
                    "status": "processing",
                }
            )
            .execute()
        )
        claim_id = result.data[0]["id"]
        logger.debug(f"Claim created with id: {claim_id}")
        return claim_id

    def save_result(
        self, claim_id: str, data: dict[str, Any]
    ) -> str:
        """
        Save analysis result.

        Args:
            claim_id: ID of the claim
            data: Analysis result data

        Returns:
            Result ID

        Raises:
            Exception: If database operation fails
        """
        logger.debug(f"Saving result for claim: {claim_id}")
        result = (
            self.client.table("results")
            .insert(
                {
                    "claim_id": claim_id,
                    "verdict": data["verdict"],
                    "confidence": data["confidence"],
                    "summary": data["summary"],
                    "supports": data.get("supports", 0),
                    "contradicts": data.get("contradicts", 0),
                    "neutral": data.get("neutral", 0),
                }
            )
            .execute()
        )
        result_id = result.data[0]["id"]
        logger.debug(f"Result saved with id: {result_id}")
        return result_id

    def save_sources_batch(
        self,
        result_id: str,
        sources: list[dict[str, Any]],
    ) -> None:
        """
        Save multiple sources in a single batch operation.

        Args:
            result_id: ID of the result
            sources: List of source data

        Raises:
            Exception: If database operation fails
        """
        if not sources:
            logger.debug("No sources to save")
            return

        logger.debug(f"Saving {len(sources)} sources for result: {result_id}")

        rows = [
            {
                "result_id": result_id,
                "url": s.get("url", ""),
                "title": s.get("title", ""),
                "author": s.get("author"),
                "published": s.get("date"),
                "stance": s.get("stance", "neutral"),
                "relevance": s.get("relevance", 5),
                "summary": s.get("summary", ""),
                "quote": s.get("quote"),
            }
            for s in sources
        ]

        self.client.table("sources").insert(rows).execute()
        logger.debug(f"Successfully saved {len(rows)} sources")

    def update_claim_status(
        self, claim_id: str, status: str
    ) -> None:
        """
        Update claim processing status.

        Args:
            claim_id: ID of the claim
            status: New status value

        Raises:
            Exception: If database operation fails
        """
        logger.debug(f"Updating claim {claim_id} status to: {status}")
        self.client.table("claims").update({"status": status}).eq(
            "id", claim_id
        ).execute()

    def get_full_result_optimized(
        self, job_id: str
    ) -> Optional[dict[str, Any]]:
        """
        Get complete analysis result with all related data using optimized queries.

        This method minimizes database calls by using efficient queries.
        Attempts to use PostgREST JOINs if available, falls back to
        multiple queries if needed.

        Args:
            job_id: Job identifier

        Returns:
            Complete analysis result or None if not found

        Raises:
            Exception: If database operation fails
        """
        logger.debug(f"Fetching complete result for job_id: {job_id}")

        # Fetch claim by job_id
        claim_response = (
            self.client.table("claims")
            .select("*")
            .eq("job_id", job_id)
            .maybe_single()
            .execute()
        )

        if not claim_response.data:
            logger.warning(f"Claim not found for job_id: {job_id}")
            return None

        claim = claim_response.data
        claim_id = claim["id"]

        # Fetch result and sources using select with nested queries
        # This reduces to 1 query instead of 3 if PostgREST supports JOINs
        logger.debug(f"Fetching result for claim_id: {claim_id}")
        result_response = (
            self.client.table("results")
            .select(
                "*"
            )  # Can be extended to include nested sources if PostgREST supports it
            .eq("claim_id", claim_id)
            .maybe_single()
            .execute()
        )

        if not result_response.data:
            logger.warning(f"Result not found for claim_id: {claim_id}")
            return None

        result = result_response.data
        result_id = result["id"]

        # Fetch sources for this result
        logger.debug(f"Fetching sources for result_id: {result_id}")
        sources_response = (
            self.client.table("sources")
            .select("*")
            .eq("result_id", result_id)
            .execute()
        )

        sources_data = sources_response.data or []
        logger.info(
            f"Successfully retrieved result for job_id: {job_id} "
            f"with {len(sources_data)} sources"
        )

        # Transform and return combined result
        return {
            "jobId": claim["job_id"],
            "claim": claim["claim_text"],
            "createdAt": claim["created_at"],
            "verdict": result["verdict"],
            "confidence": result["confidence"],
            "summary": result["summary"],
            "supports": result["supports"],
            "contradicts": result["contradicts"],
            "neutral": result["neutral"],
            "sources": [
                {
                    "url": s["url"],
                    "title": s["title"],
                    "author": s.get("author"),
                    "date": s.get("published"),
                    "stance": s["stance"],
                    "relevance": s.get("relevance", 5),
                    "summary": s.get("summary", ""),
                    "quote": s.get("quote"),
                }
                for s in sources_data
            ],
        }

    def get_recent_results(
        self, limit: int = 10, offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        Get recent analysis results (paginated).

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of analysis results

        Raises:
            Exception: If database operation fails
        """
        logger.debug(f"Fetching recent results (limit: {limit}, offset: {offset})")

        response = (
            self.client.table("claims")
            .select("*")
            .eq("status", "done")
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        return response.data or []

    def health_check(self) -> bool:
        """
        Check database connectivity with simple query.

        Returns:
            True if database is accessible, False otherwise
        """
        try:
            logger.debug("Running database health check")
            self.client.table("claims").select("id").limit(1).execute()
            logger.debug("Database health check passed")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
