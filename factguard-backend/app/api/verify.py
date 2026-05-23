from fastapi import APIRouter
from pydantic import BaseModel

from app.services.gemini import (
    analyze_claim,
)

router = APIRouter()


class VerifyRequest(
    BaseModel
):
    claim: str


@router.post("/verify")
async def verify(
    payload: VerifyRequest
):
    result = (
        await analyze_claim(
            payload.claim
        )
    )

    return result