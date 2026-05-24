"""
Request and response schema definitions for FactGuard API.
Uses Pydantic for validation and type safety.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VerifyRequest(BaseModel):
    """Request schema for claim verification endpoint."""

    claim: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="The claim to verify",
        example="The Earth is flat",
    )

    class Config:
        json_schema_extra = {
            "example": {"claim": "COVID-19 vaccines contain microchips"}
        }


class SourceResponse(BaseModel):
    """Response schema for a single source in analysis results."""

    url: str = Field(..., description="URL of the source")
    title: str = Field(..., description="Title of the source article")
    author: Optional[str] = Field(
        None, description="Author or organization name"
    )
    date: Optional[str] = Field(None, description="Publication date")
    stance: str = Field(
        ...,
        description="Stance of source relative to claim",
        example="supports",
    )
    summary: str = Field(
        ..., description="Brief explanation of source content"
    )
    quote: Optional[str] = Field(
        None, description="Relevant quote from the source"
    )
    relevance: int = Field(
        default=5,
        ge=0,
        le=10,
        description="Relevance score (0-10)",
    )


class AnalysisResponse(BaseModel):
    """Response schema for claim analysis."""

    jobId: str = Field(..., description="Unique job ID for tracking")
    claim: str = Field(..., description="The original claim analyzed")
    createdAt: str = Field(
        ..., description="ISO-8601 timestamp of analysis"
    )
    verdict: str = Field(
        ...,
        description="Analysis verdict",
        example="Likely Misleading",
    )
    confidence: str = Field(
        ...,
        description="Confidence level in verdict",
        example="High",
    )
    summary: str = Field(
        ...,
        description="2-3 sentence explanation of analysis",
    )
    supports: int = Field(
        ..., ge=0, description="Number of supporting sources"
    )
    contradicts: int = Field(
        ..., ge=0, description="Number of contradicting sources"
    )
    neutral: int = Field(
        ..., ge=0, description="Number of neutral sources"
    )
    sources: list[SourceResponse] = Field(
        default_factory=list,
        description="List of sources used in analysis",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "jobId": "550e8400-e29b-41d4-a716-446655440000",
                "claim": "The Earth is flat",
                "createdAt": "2026-05-24T10:30:00Z",
                "verdict": "Likely Misleading",
                "confidence": "High",
                "summary": "Scientific consensus strongly contradicts this claim. "
                "Multiple lines of evidence prove the Earth is spherical.",
                "supports": 0,
                "contradicts": 8,
                "neutral": 2,
                "sources": [
                    {
                        "url": "https://example.com/science",
                        "title": "Proof the Earth is Spherical",
                        "author": "NASA",
                        "date": "2026-05-20",
                        "stance": "contradicts",
                        "summary": "Scientific evidence...",
                        "quote": "The Earth is a sphere...",
                        "relevance": 10,
                    }
                ],
            }
        }


class HealthCheckResponse(BaseModel):
    """Response schema for health check endpoint."""

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")


class DetailedHealthCheckResponse(BaseModel):
    """Response schema for detailed health check endpoint."""

    status: str = Field(..., description="Overall health status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
    database: Optional[str] = Field(
        None, description="Database connection status"
    )
    gemini_api: Optional[str] = Field(
        None, description="Gemini API status"
    )


class ErrorResponse(BaseModel):
    """Response schema for error responses."""

    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict = Field(
        default_factory=dict,
        description="Additional error details",
    )


class PaginatedSourcesResponse(BaseModel):
    """Response schema for paginated sources."""

    total: int = Field(..., description="Total number of sources")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    sources: list[SourceResponse] = Field(
        ..., description="Sources on current page"
    )
