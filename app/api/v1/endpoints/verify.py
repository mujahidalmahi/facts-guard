"""
Claim verification endpoints for FactGuard API v1.
Handles fact-checking and misinformation detection.
"""

import uuid
import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from google.api_core.exceptions import ResourceExhausted

from app.schemas import VerifyRequest, AnalysisResponse
from app.exceptions import (
    AnalysisFailedError,
    ClaimNotFoundError,
    DatabaseError,
    GeminiAPIError,
)
from app.logging_config import get_logger
from app.dependencies import (
    get_gemini_service_instance,
    get_supabase_service_instance,
)

logger = get_logger("verify_endpoint")

router = APIRouter()


async def analyze_claim_with_fallback(
    claim: str,
    gemini_service,
    max_retries: int = 3,
) -> dict:
    """
    Analyze a claim using Gemini API with automatic key rotation on failure.
    
    Args:
        claim: The claim text to analyze
        gemini_service: Gemini service instance
        max_retries: Maximum number of retries with different keys
        
    Returns:
        Analysis result dictionary
        
    Raises:
        GeminiAPIError: If all API keys are exhausted
    """
    prompt = f"""
You are FactGuard, an AI misinformation detection system.

Analyze the following claim carefully.

CLAIM:
"{claim}"

Return ONLY valid JSON.

Rules:
- Do not include markdown
- Do not wrap response in ```json
- Be concise
- Generate realistic evidence entries
- stance must be:
  supports | contradicts | neutral

JSON format:

{{
  "verdict": "Verified | Likely True | Mixed Evidence | Likely Misleading | Unverified",
  "confidence": "Low | Medium | High",
  "summary": "2 sentence explanation",

  "supports": number,
  "contradicts": number,
  "neutral": number,

  "sources": [
    {{
      "title": "source title",
      "url": "https://example.com",
      "author": "organization name",
      "date": "2026-05-23",
      "stance": "contradicts",
      "summary": "short explanation",
      "quote": "short quote"
    }}
  ]
}}
"""

    import json

    last_error = None

    for attempt in range(max_retries):
        try:
            logger.debug(
                f"Attempting Gemini API call (attempt {attempt + 1}/{max_retries})"
            )

            model = gemini_service.get_model()
            response = await asyncio.to_thread(
                model.generate_content, prompt
            )

            text = (
                response.text.replace("```json", "")
                .replace("```", "")
                .strip()
            )

            result = json.loads(text)
            logger.info("Claim analysis completed successfully")
            return result

        except ResourceExhausted as e:
            last_error = e
            logger.warning(
                f"Gemini API key exhausted (attempt {attempt + 1}/{max_retries}), "
                f"rotating to next key"
            )
            try:
                gemini_service.rotate_key()
            except Exception as rotate_error:
                logger.error(f"Failed to rotate API key: {rotate_error}")
                raise GeminiAPIError(
                    f"API key rotation failed: {str(rotate_error)}"
                )
            continue

        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {str(e)}, returning default")
            return {
                "verdict": "Unverified",
                "confidence": "Low",
                "summary": "Could not parse analysis response. Please try again.",
                "supports": 0,
                "contradicts": 0,
                "neutral": 0,
                "sources": [],
            }

        except Exception as e:
            logger.error(f"Unexpected error during analysis: {str(e)}")
            raise GeminiAPIError(f"Unexpected error: {str(e)}")

    # All retries exhausted
    logger.error("All API key retries exhausted")
    raise GeminiAPIError(
        f"All API keys exhausted after {max_retries} attempts. "
        f"Last error: {str(last_error)}"
    )


@router.post(
    "",
    response_model=AnalysisResponse,
    summary="Verify a claim",
    description="Submit a claim for fact-checking and misinformation detection",
)
async def verify(
    payload: VerifyRequest,
    gemini_service=Depends(get_gemini_service_instance),
    supabase_service=Depends(get_supabase_service_instance),
) -> AnalysisResponse:
    """
    Verify a claim and return analysis results.
    
    This endpoint accepts a claim, analyzes it using Gemini AI,
    stores the results in the database, and returns the analysis.
    
    Args:
        payload: Request containing the claim text
        gemini_service: Injected Gemini service
        supabase_service: Injected Supabase service
        
    Returns:
        AnalysisResponse with verdict, confidence, sources, etc.
        
    Raises:
        ValidationError: If claim text is invalid
        AnalysisFailedError: If analysis fails
        DatabaseError: If database operations fail
    """
    job_id = str(uuid.uuid4())
    logger.info(f"Started claim verification (job_id: {job_id})")

    try:
        client = supabase_service.get_client()

        # Create claim record
        logger.debug("Creating claim record in database")
        try:
            claim_result = (
                client.table("claims")
                .insert(
                    {
                        "claim_text": payload.claim,
                        "job_id": job_id,
                        "status": "processing",
                    }
                )
                .execute()
            )
            claim_id = claim_result.data[0]["id"]
            logger.debug(f"Claim created with id: {claim_id}")
        except Exception as e:
            logger.error(f"Failed to create claim record: {str(e)}")
            raise DatabaseError(
                f"Failed to create claim record: {str(e)}"
            )

        # Analyze claim
        logger.debug("Starting claim analysis")
        analysis_result = await analyze_claim_with_fallback(
            payload.claim, gemini_service
        )

        # Save analysis result
        logger.debug("Saving analysis result to database")
        try:
            result_response = (
                client.table("results")
                .insert(
                    {
                        "claim_id": claim_id,
                        "verdict": analysis_result["verdict"],
                        "confidence": analysis_result["confidence"],
                        "summary": analysis_result["summary"],
                        "supports": analysis_result.get("supports", 0),
                        "contradicts": analysis_result.get(
                            "contradicts", 0
                        ),
                        "neutral": analysis_result.get("neutral", 0),
                    }
                )
                .execute()
            )
            result_id = result_response.data[0]["id"]
            logger.debug(f"Result saved with id: {result_id}")
        except Exception as e:
            logger.error(f"Failed to save analysis result: {str(e)}")
            raise DatabaseError(
                f"Failed to save analysis result: {str(e)}"
            )

        # Save sources
        sources = analysis_result.get("sources", [])
        if sources:
            logger.debug(f"Saving {len(sources)} sources to database")
            try:
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
                client.table("sources").insert(rows).execute()
                logger.debug(f"Successfully saved {len(rows)} sources")
            except Exception as e:
                logger.error(f"Failed to save sources: {str(e)}")
                raise DatabaseError(f"Failed to save sources: {str(e)}")

        # Update claim status
        logger.debug("Updating claim status to 'done'")
        try:
            client.table("claims").update({"status": "done"}).eq(
                "id", claim_id
            ).execute()
        except Exception as e:
            logger.error(f"Failed to update claim status: {str(e)}")
            # Log but don't raise - status update failure shouldn't block response

        logger.info(
            f"Claim verification completed successfully (job_id: {job_id})"
        )

        return AnalysisResponse(
            jobId=job_id,
            claim=payload.claim,
            createdAt=datetime.now(timezone.utc).isoformat(),
            verdict=analysis_result["verdict"],
            confidence=analysis_result["confidence"],
            summary=analysis_result["summary"],
            supports=analysis_result.get("supports", 0),
            contradicts=analysis_result.get("contradicts", 0),
            neutral=analysis_result.get("neutral", 0),
            sources=[
                {
                    "url": s.get("url", ""),
                    "title": s.get("title", ""),
                    "author": s.get("author"),
                    "date": s.get("date"),
                    "stance": s.get("stance", "neutral"),
                    "summary": s.get("summary", ""),
                    "quote": s.get("quote"),
                    "relevance": s.get("relevance", 5),
                }
                for s in sources
            ],
        )

    except (AnalysisFailedError, DatabaseError, GeminiAPIError):
        # Re-raise known exceptions
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error during claim verification: {str(e)}"
        )
        raise AnalysisFailedError(f"Unexpected error: {str(e)}")


@router.get(
    "/{job_id}",
    response_model=AnalysisResponse,
    summary="Get verification result",
    description="Retrieve previously analyzed claim results by job ID",
)
async def get_result(
    job_id: str,
    supabase_service=Depends(get_supabase_service_instance),
) -> AnalysisResponse:
    """
    Retrieve analysis results for a previously verified claim.
    
    Args:
        job_id: The job ID returned from the verify endpoint
        supabase_service: Injected Supabase service
        
    Returns:
        AnalysisResponse with stored results
        
    Raises:
        ClaimNotFoundError: If claim/result not found
        DatabaseError: If database query fails
    """
    logger.info(f"Retrieving result for job_id: {job_id}")

    try:
        client = supabase_service.get_client()

        # Query claim
        logger.debug(f"Querying claim with job_id: {job_id}")
        claim_response = (
            client.table("claims")
            .select("*")
            .eq("job_id", job_id)
            .maybe_single()
            .execute()
        )

        if not claim_response.data:
            logger.warning(f"Claim not found for job_id: {job_id}")
            raise ClaimNotFoundError(job_id)

        claim = claim_response.data
        claim_id = claim["id"]

        # Query result
        logger.debug(f"Querying result for claim_id: {claim_id}")
        result_response = (
            client.table("results")
            .select("*")
            .eq("claim_id", claim_id)
            .maybe_single()
            .execute()
        )

        if not result_response.data:
            logger.warning(f"Result not found for claim_id: {claim_id}")
            raise ClaimNotFoundError(job_id)

        result = result_response.data
        result_id = result["id"]

        # Query sources
        logger.debug(f"Querying sources for result_id: {result_id}")
        sources_response = (
            client.table("sources")
            .select("*")
            .eq("result_id", result_id)
            .execute()
        )

        sources_data = sources_response.data or []
        logger.info(
            f"Successfully retrieved result for job_id: {job_id} "
            f"({len(sources_data)} sources)"
        )

        return AnalysisResponse(
            jobId=claim["job_id"],
            claim=claim["claim_text"],
            createdAt=claim["created_at"],
            verdict=result["verdict"],
            confidence=result["confidence"],
            summary=result["summary"],
            supports=result["supports"],
            contradicts=result["contradicts"],
            neutral=result["neutral"],
            sources=[
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
        )

    except ClaimNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving result for job_id {job_id}: {str(e)}")
        raise DatabaseError(f"Failed to retrieve result: {str(e)}")
