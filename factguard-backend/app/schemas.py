from typing import Optional

from pydantic import BaseModel, Field, field_validator
from typing_extensions import Literal

from app.utils.validators import contains_sql_injection_pattern


class VerifyRequest(BaseModel):
    claim: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="The claim to verify",
    )

    @field_validator("claim")
    @classmethod
    def validate_claim(cls, v: str) -> str:
        if contains_sql_injection_pattern(v):
            raise ValueError("Claim contains invalid characters or patterns")
        return v


class SourceResponse(BaseModel):
    url: str = Field(..., description="URL of the source")
    title: str = Field(..., description="Title of the source article")
    author: Optional[str] = Field(None, description="Author or organization name")
    date: Optional[str] = Field(None, description="Publication date")
    stance: str = Field(..., description="Stance relative to claim")
    summary: str = Field(..., description="Brief explanation of source content")
    quote: Optional[str] = Field(None, description="Relevant quote")
    relevance: int = Field(default=5, ge=0, le=10, description="Relevance score (0-10)")


class AnalysisResponse(BaseModel):
    jobId: str = Field(..., description="Unique job ID for tracking")
    claim: str = Field(..., description="The original claim analyzed")
    createdAt: str = Field(..., description="ISO-8601 timestamp")
    verdict: str = Field(..., description="Analysis verdict")
    confidence: str = Field(..., description="Confidence level")
    summary: str = Field(..., description="Explanation of analysis")
    supports: int = Field(..., ge=0, description="Number of supporting sources")
    contradicts: int = Field(..., ge=0, description="Number of contradicting sources")
    neutral: int = Field(..., ge=0, description="Number of neutral sources")
    sources: list[SourceResponse] = Field(
        default_factory=list,
        description="List of sources used in analysis",
    )


class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")


class ProductListingResponse(BaseModel):
    title: str = Field(..., description="Product title")
    price: Optional[float] = Field(None, description="Price amount")
    currency: str = Field("USD", description="Currency code")
    merchant: str = Field(..., description="Merchant name")
    trustLevel: str = Field("Medium", description="Merchant trust level (High/Medium/Low)")
    url: str = Field(..., description="Product URL")
    image: Optional[str] = Field(None, description="Product image URL")
    condition: Optional[str] = Field(None, description="Product condition")


class ProductVariantResponse(BaseModel):
    model: str = Field(..., description="Model/variant name")
    specs: Optional[str] = Field(None, description="Key specifications")
    priceRange: str = Field(..., description="Price range across listings")


class PriceCheckRequest(BaseModel):
    product: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Product name to compare prices for",
    )

    @field_validator("product")
    @classmethod
    def validate_product(cls, v: str) -> str:
        if contains_sql_injection_pattern(v):
            raise ValueError("Product name contains invalid characters or patterns")
        return v


class PriceCheckResponse(BaseModel):
    status: str = Field(..., description="Status of the price check")
    jobId: str = Field(..., description="Unique job ID for tracking")
    product: Optional[str] = Field(None, description="The original product name")
    createdAt: Optional[str] = Field(None, description="ISO-8601 timestamp")
    listings: list[ProductListingResponse] = Field(
        default_factory=list, description="Product listings from various merchants"
    )
    variants: list[ProductVariantResponse] = Field(
        default_factory=list, description="Detected product models/variants"
    )


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict = Field(
        default_factory=dict,
        description="Additional error details",
    )


class JobResponse(BaseModel):
    jobId: str = Field(..., description="Unique job ID for tracking")


class ProcessingResult(BaseModel):
    status: Literal["processing", "done", "error"] = Field(..., description="Job status")
    jobId: str = Field(..., description="Unique job ID for tracking")


class FinancialRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="Financial query",
    )

    @field_validator("query")
    @classmethod
    def validate_query(
        cls,
        v: str,
    ) -> str:
        if contains_sql_injection_pattern(v):
            raise ValueError("Invalid query")

        return v
