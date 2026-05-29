import pytest


@pytest.fixture
def sample_claim() -> str:
    return "The Earth is flat"


@pytest.fixture
def sample_claim_result() -> dict:
    return {
        "verdict": "Unverified",
        "confidence": "Low",
        "summary": "Test summary",
        "supports": 0,
        "contradicts": 0,
        "neutral": 0,
        "sources": [],
    }
